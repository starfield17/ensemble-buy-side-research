from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import load_settings, now_utc
from ..infrastructure.connectors import akshare, news, sec, tushare, yfinance
from ..io import ensure_dir, read_json, save_table_formats, write_json
from ..models import RunManifest, SourceRecord
from ..security import infer_market, normalize_symbol

DATASET_COLUMNS = {
    "prices": ["symbol", "date", "open", "high", "low", "close", "volume", "currency", "provider", "adjustment"],
    "fundamentals": [
        "symbol", "company", "as_of", "currency", "fiscal_window", "price", "shares_outstanding",
        "market_cap", "enterprise_value", "revenue_ttm", "net_income_ttm", "book_value",
        "ebitda_ttm", "gross_profit_ttm", "operating_income_ttm", "operating_cash_flow_ttm",
        "capex_ttm", "free_cash_flow_ttm", "total_debt", "cash", "minority_interest",
        "eps_ttm", "eps_ttm_diluted", "eps_ttm_ex_items", "eps_last_fy", "book_value_per_share",
        "forward_eps", "eps_growth_3y_cagr", "eps_growth_5y_cagr", "analyst_eps_growth_5y", "provider",
    ],
    "etf_snapshot": [
        "symbol", "name", "as_of", "timestamp", "currency", "market_price", "iopv", "nav",
        "provider_reported_premium_pct", "cross_border", "provider",
    ],
    "filings": ["symbol", "company", "form", "filing_date", "report_date", "accession", "url", "provider"],
    "news": ["id", "query", "title", "url", "publisher", "published_at", "language", "source_country", "provider", "retrieved_on"],
}


def _empty(dataset: str) -> pd.DataFrame:
    return pd.DataFrame(columns=DATASET_COLUMNS[dataset])


def _combine(frames: list[pd.DataFrame], dataset: str) -> pd.DataFrame:
    available = [frame for frame in frames if frame is not None and not frame.empty]
    if not available:
        return _empty(dataset)
    result = pd.concat(available, ignore_index=True, sort=False)
    for column in DATASET_COLUMNS[dataset]:
        if column not in result.columns:
            result[column] = None
    result = result[DATASET_COLUMNS[dataset]]
    if dataset == "prices":
        result = result.drop_duplicates(["symbol", "date", "provider"], keep="last").sort_values(["symbol", "date"])
    elif dataset in {"fundamentals", "etf_snapshot"}:
        result = result.drop_duplicates(["symbol", "provider"], keep="last")
    return result.reset_index(drop=True)


def load_manifest(run_dir: str | Path) -> RunManifest:
    path = Path(run_dir) / "manifest.json"
    if path.exists():
        return RunManifest.model_validate(read_json(path))
    return RunManifest()


def save_manifest(run_dir: str | Path, manifest: RunManifest) -> Path:
    manifest.updated_at = now_utc()
    return write_json(Path(run_dir) / "manifest.json", manifest)


def _append_sources(manifest: RunManifest, records: list[SourceRecord]) -> None:
    manifest.sources.extend(records)
    for record in records:
        manifest.errors.extend(record.errors)


def fetch_data(
    run_dir: str | Path,
    symbols: list[str],
    datasets: list[str],
    *,
    provider: str = "auto",
    start: str | None = None,
    end: str | None = None,
    query: str | None = None,
    formats: list[str] | None = None,
) -> RunManifest:
    run_dir = ensure_dir(run_dir)
    formats = formats or ["csv"]
    symbols = [normalize_symbol(symbol) for symbol in symbols]
    datasets = [dataset.strip().lower() for dataset in datasets]
    settings = load_settings()
    manifest = RunManifest(symbols=symbols, query=query, requested_datasets=datasets, status="running")
    frames: dict[str, list[pd.DataFrame]] = {name: [] for name in DATASET_COLUMNS}

    cn_symbols = [symbol for symbol in symbols if infer_market(symbol) == "CN"]
    non_cn_symbols = [symbol for symbol in symbols if infer_market(symbol) != "CN"]
    us_symbols = [symbol for symbol in symbols if infer_market(symbol) == "US"]

    if "prices" in datasets:
        if provider in {"auto", "akshare"} and cn_symbols:
            frame, records = akshare.fetch_prices(cn_symbols, start, end)
            frames["prices"].append(frame); _append_sources(manifest, records)
        if provider in {"auto", "yfinance"}:
            targets = non_cn_symbols if provider == "auto" else symbols
            if targets:
                frame, records = yfinance.fetch_prices(targets, start, end)
                frames["prices"].append(frame); _append_sources(manifest, records)
        if provider == "tushare":
            manifest.notes.append("Tushare price fetching is not implemented; use AKShare or yfinance.")

    if "fundamentals" in datasets:
        if provider in {"auto", "tushare"} and cn_symbols and settings.tushare_token:
            frame, records = tushare.fetch_fundamentals(cn_symbols, settings.tushare_token)
            frames["fundamentals"].append(frame); _append_sources(manifest, records)
        elif provider == "tushare":
            frame, records = tushare.fetch_fundamentals(symbols, settings.tushare_token)
            frames["fundamentals"].append(frame); _append_sources(manifest, records)
        if provider in {"auto", "yfinance"}:
            targets = symbols if provider == "yfinance" else non_cn_symbols + (cn_symbols if not settings.tushare_token else [])
            if targets:
                frame, records = yfinance.fetch_fundamentals(targets)
                frames["fundamentals"].append(frame); _append_sources(manifest, records)

    if "etf" in datasets or "etf_snapshot" in datasets:
        if provider in {"auto", "akshare"} and cn_symbols:
            frame, records = akshare.fetch_etf_snapshot(cn_symbols)
            frames["etf_snapshot"].append(frame); _append_sources(manifest, records)
        if provider in {"auto", "yfinance"}:
            targets = non_cn_symbols if provider == "auto" else symbols
            if targets:
                frame, records = yfinance.fetch_etf_snapshot(targets)
                frames["etf_snapshot"].append(frame); _append_sources(manifest, records)

    if "etf_prices" in datasets and cn_symbols:
        frame, records = akshare.fetch_prices(cn_symbols, start, end, etf=True)
        frames["prices"].append(frame); _append_sources(manifest, records)

    if "filings" in datasets:
        targets = us_symbols if provider == "auto" else symbols
        frame, records = sec.fetch_filings(targets, settings.sec_user_agent, settings.request_timeout)
        frames["filings"].append(frame); _append_sources(manifest, records)

    if "news" in datasets:
        if not query:
            manifest.notes.append("News requested without --query; skipped.")
        else:
            frame, records = news.fetch_news(query, start, end, settings.request_timeout)
            frames["news"].append(frame); _append_sources(manifest, records)

    requested_stems: list[str] = []
    for dataset in datasets:
        stem = "etf_snapshot" if dataset == "etf" else ("prices" if dataset == "etf_prices" else dataset)
        if stem in DATASET_COLUMNS and stem not in requested_stems:
            requested_stems.append(stem)
    for stem in requested_stems:
        frame = _combine(frames[stem], stem)
        artifacts, warnings = save_table_formats(run_dir, stem, frame, formats)
        manifest.artifacts.update(artifacts)
        manifest.notes.extend(warnings)

    has_failure = any(source.status == "failed" for source in manifest.sources)
    has_warning = any(source.status in {"partial", "unsupported"} for source in manifest.sources)
    all_failed = bool(manifest.sources) and all(source.status == "failed" for source in manifest.sources)
    manifest.status = "failed" if all_failed else ("completed_with_warnings" if has_failure or has_warning or manifest.notes else "completed")
    if not manifest.sources and requested_stems:
        manifest.status = "failed"
        manifest.notes.append("No connector was executed for the requested dataset/provider combination.")
    save_manifest(run_dir, manifest)
    return manifest
