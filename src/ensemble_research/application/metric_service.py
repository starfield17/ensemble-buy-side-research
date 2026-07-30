from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pandas as pd

from ..domain.metrics import calculate_etf_metrics, calculate_fundamental_metrics, calculate_performance_metrics
from ..io import first_existing, read_frame, write_frame, write_json
from ..models import MetricRecord

METRIC_DEFINITIONS = {
    "pe_ttm": "market cap / TTM net income; fallback price / diluted TTM EPS",
    "pe_ttm_ex_items": "price / diluted TTM EPS excluding non-recurring items",
    "pe_static": "price / last full-year diluted EPS",
    "pe_forward": "price / forward consensus EPS",
    "pb": "market cap / common equity; fallback price / book value per share",
    "ps_ttm": "market cap / TTM revenue",
    "ev_ebitda": "enterprise value / TTM EBITDA; EV includes minority interest when available",
    "fcf_yield": "TTM free cash flow / market cap * 100",
    "roe": "TTM net income / common equity * 100",
    "debt_to_equity": "interest-bearing debt / common equity",
    "gross_margin": "TTM gross profit / TTM revenue * 100",
    "operating_margin": "TTM operating income / TTM revenue * 100",
    "peg_historical_3y": "PE(TTM) / 3-year historical EPS CAGR percentage points",
    "peg_historical_5y": "PE(TTM) / 5-year historical EPS CAGR percentage points",
    "peg_forward_consensus": "PE(TTM) / consensus 5-year EPS growth percentage points",
    "peg_custom": "PE(TTM) / analyst-supplied growth percentage points",
    "premium_to_iopv": "(market price / IOPV - 1) * 100",
    "premium_to_nav": "(market price / official NAV - 1) * 100",
    "period_return": "(last close / first close - 1) * 100",
    "annualized_volatility": "sample std(daily returns) * sqrt(252) * 100",
    "max_drawdown": "min(close / cumulative max(close) - 1) * 100",
}


def calculate_metrics(
    run_dir: str | Path,
    output_format: str = "csv",
    *,
    custom_growth_rates: Mapping[str, float] | None = None,
    cross_market: bool = False,
) -> tuple[pd.DataFrame, list[str]]:
    run_dir = Path(run_dir)
    records: list[MetricRecord] = []
    warnings: list[str] = []
    fundamentals = first_existing(run_dir, "fundamentals")
    prices = first_existing(run_dir, "prices")
    etf = first_existing(run_dir, "etf_snapshot")
    if fundamentals:
        records.extend(calculate_fundamental_metrics(read_frame(fundamentals), custom_growth_rates=custom_growth_rates, cross_market=cross_market))
    else:
        warnings.append("No fundamentals dataset found; company metrics were skipped.")
    if prices:
        records.extend(calculate_performance_metrics(read_frame(prices)))
    else:
        warnings.append("No prices dataset found; performance metrics were skipped.")
    if etf:
        records.extend(calculate_etf_metrics(read_frame(etf)))
    else:
        warnings.append("No ETF snapshot found; ETF premium metrics were skipped.")
    frame = pd.DataFrame([record.model_dump() for record in records])
    storage = frame.copy()
    if not storage.empty:
        storage["inputs"] = storage["inputs"].map(lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, default=str))
        storage["caveats"] = storage["caveats"].map(lambda value: json.dumps(value, ensure_ascii=False))
    write_frame(run_dir / "metrics" / f"metrics.{output_format}", storage)
    write_json(run_dir / "metrics" / "metric_definitions.json", METRIC_DEFINITIONS)
    return frame, warnings
