"""Trading-day event studies with raw, market-adjusted, or market-model returns."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

DEFAULT_WINDOWS = [(-1, 1), (0, 5), (0, 20), (0, 60)]


def _normalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    work = prices.copy()
    if "symbol" not in work.columns and "ticker" in work.columns:
        work = work.rename(columns={"ticker": "symbol"})
    required = {"symbol", "date", "close"}
    missing = required - set(work.columns)
    if missing:
        raise ValueError(f"prices missing required columns: {sorted(missing)}")
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work["close"] = pd.to_numeric(work["close"], errors="coerce")
    return work.dropna(subset=["symbol", "date", "close"]).sort_values(["symbol", "date"])


def _returns_by_symbol(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    result: dict[str, pd.DataFrame] = {}
    for symbol, group in _normalize_prices(prices).groupby("symbol"):
        group = group.drop_duplicates("date", keep="last").sort_values("date").copy()
        group["return"] = group["close"].pct_change()
        result[str(symbol)] = group.reset_index(drop=True)
    return result


def _anchor_index(series: pd.DataFrame, event_date: pd.Timestamp) -> int | None:
    matches = series.index[series["date"] >= event_date]
    return int(matches[0]) if len(matches) else None


def _cumulative(series: pd.DataFrame, start: int, end: int) -> float | None:
    if start < 0 or end >= len(series) or start > end:
        return None
    window = pd.to_numeric(series["return"].iloc[start : end + 1], errors="coerce").dropna()
    if window.empty:
        return None
    return float((1.0 + window).prod() - 1.0)


def _market_model_params(asset: pd.DataFrame, benchmark: pd.DataFrame, anchor: int, minimum: int = 60) -> tuple[float, float, int] | None:
    estimation_end = anchor - 10
    estimation_start = max(1, estimation_end - 120)
    if estimation_end <= estimation_start:
        return None
    left = asset.iloc[estimation_start:estimation_end][["date", "return"]].rename(columns={"return": "asset_return"})
    right = benchmark[["date", "return"]].rename(columns={"return": "benchmark_return"})
    merged = left.merge(right, on="date", how="inner").dropna()
    if len(merged) < minimum:
        return None
    x = merged["benchmark_return"].to_numpy(dtype=float)
    y = merged["asset_return"].to_numpy(dtype=float)
    beta, alpha = np.polyfit(x, y, 1)
    return float(alpha), float(beta), int(len(merged))


def run_event_study(
    events: Iterable[Mapping[str, Any]],
    prices: pd.DataFrame,
    *,
    benchmark: str | None = None,
    model: str = "market_adjusted",
    windows: list[tuple[int, int]] | None = None,
) -> pd.DataFrame:
    model = model.replace("-", "_")
    if model not in {"market_adjusted", "market_model", "raw"}:
        raise ValueError("model must be raw, market-adjusted, or market-model")
    windows = windows or DEFAULT_WINDOWS
    by_symbol = _returns_by_symbol(prices)
    bench = by_symbol.get(str(benchmark)) if benchmark else None
    rows: list[dict[str, Any]] = []
    for event in events:
        raw_date = event.get("date") or event.get("event_date")
        if raw_date is None:
            continue
        event_date = pd.to_datetime(raw_date)
        symbols = event.get("symbols") or event.get("tickers") or event.get("symbol") or event.get("ticker") or []
        if isinstance(symbols, str):
            symbols = [symbols]
        for symbol in symbols:
            asset = by_symbol.get(str(symbol))
            if asset is None or asset.empty:
                continue
            anchor = _anchor_index(asset, event_date)
            if anchor is None:
                continue
            anchor_date = asset["date"].iloc[anchor]
            effective = model
            params = None
            notes: list[str] = []
            if model == "market_model" and bench is not None:
                params = _market_model_params(asset, bench, anchor)
                if params is None:
                    effective = "market_adjusted"
                    notes.append("Insufficient clean estimation history for the market model; fell back to market adjustment.")
            if bench is None and model != "raw":
                effective = "raw"
                notes.append("No benchmark supplied; returns are raw, not abnormal.")
            if anchor_date.normalize() != event_date.normalize():
                notes.append(f"Event date {event_date.date()} was not a trading session; anchored to {anchor_date.date()}.")
            benchmark_anchor = _anchor_index(bench, event_date) if bench is not None else None
            for start_offset, end_offset in windows:
                raw_return = _cumulative(asset, anchor + start_offset, anchor + end_offset)
                if raw_return is None:
                    continue
                benchmark_return = None
                if bench is not None and benchmark_anchor is not None:
                    benchmark_return = _cumulative(bench, benchmark_anchor + start_offset, benchmark_anchor + end_offset)
                if effective == "raw" or benchmark_return is None:
                    abnormal = None
                elif effective == "market_model" and params is not None:
                    alpha, beta, _ = params
                    expected = alpha * (end_offset - start_offset + 1) + beta * benchmark_return
                    abnormal = raw_return - expected
                else:
                    abnormal = raw_return - benchmark_return
                rows.append({
                    "event_id": event.get("id") or event.get("title") or "event",
                    "symbol": str(symbol), "event_date": event_date.date().isoformat(),
                    "anchor_date": anchor_date.date().isoformat(),
                    "window": f"[{start_offset},{end_offset}] trading days", "model": effective,
                    "benchmark": benchmark, "raw_return_pct": raw_return * 100.0,
                    "benchmark_return_pct": benchmark_return * 100.0 if benchmark_return is not None else None,
                    "abnormal_return_pct": abnormal * 100.0 if abnormal is not None else None,
                    "alpha_daily": params[0] if params else None, "beta": params[1] if params else None,
                    "estimation_days": params[2] if params else None, "note": "; ".join(notes) or None,
                })
    return pd.DataFrame(rows, columns=[
        "event_id", "symbol", "event_date", "anchor_date", "window", "model", "benchmark",
        "raw_return_pct", "benchmark_return_pct", "abnormal_return_pct", "alpha_daily", "beta",
        "estimation_days", "note",
    ])
