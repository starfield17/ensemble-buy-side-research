"""Historical valuation series and percentile calculations."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

LOOKAHEAD_CAVEAT = (
    "Point-in-time quality depends on the supplied fundamentals. Restatements and reporting lags "
    "can make an as-reported-now historical multiple series optimistic; treat the percentile as indicative."
)
MIN_OBSERVATIONS = 60


def _symbol_column(frame: pd.DataFrame) -> str:
    if "symbol" in frame.columns:
        return "symbol"
    if "ticker" in frame.columns:
        return "ticker"
    raise ValueError("input must contain symbol or ticker")


def build_multiple_series(
    prices: pd.DataFrame,
    fundamentals: pd.DataFrame,
    *,
    symbol: str,
    metric: str = "pe_ttm",
) -> pd.DataFrame:
    """Backward-join each price to the most recent prior reported fundamental observation."""
    price_symbol = _symbol_column(prices)
    fund_symbol = _symbol_column(fundamentals)
    p = prices[prices[price_symbol].astype(str) == str(symbol)].copy()
    f = fundamentals[fundamentals[fund_symbol].astype(str) == str(symbol)].copy()
    if p.empty or f.empty:
        return pd.DataFrame(columns=["symbol", "date", "close", "denominator", "multiple", "metric"])
    p["date"] = pd.to_datetime(p["date"], errors="coerce")
    f["date"] = pd.to_datetime(f["as_of"] if "as_of" in f.columns else f["date"], errors="coerce")
    p["close"] = pd.to_numeric(p["close"], errors="coerce")
    p = p.dropna(subset=["date", "close"]).sort_values("date")
    f = f.dropna(subset=["date"]).sort_values("date")

    if metric == "pe_ttm":
        if "eps_ttm_diluted" in f.columns:
            denominator = "eps_ttm_diluted"
        elif "eps_ttm" in f.columns:
            denominator = "eps_ttm"
        elif {"net_income_ttm", "shares_outstanding"}.issubset(f.columns):
            f["_eps_derived"] = pd.to_numeric(f["net_income_ttm"], errors="coerce") / pd.to_numeric(f["shares_outstanding"], errors="coerce")
            denominator = "_eps_derived"
        else:
            raise ValueError("PE percentile requires eps_ttm_diluted, eps_ttm, or net_income_ttm + shares_outstanding")
        method = "close / most recent prior diluted TTM EPS"
    elif metric == "pb":
        if "book_value_per_share" in f.columns:
            denominator = "book_value_per_share"
        elif "bvps" in f.columns:
            denominator = "bvps"
        elif {"book_value", "shares_outstanding"}.issubset(f.columns):
            f["_bvps_derived"] = pd.to_numeric(f["book_value"], errors="coerce") / pd.to_numeric(f["shares_outstanding"], errors="coerce")
            denominator = "_bvps_derived"
        else:
            raise ValueError("PB percentile requires book value per share or book_value + shares_outstanding")
        method = "close / most recent prior book value per share"
    elif metric == "ps_ttm":
        if "revenue_per_share_ttm" in f.columns:
            denominator = "revenue_per_share_ttm"
        elif {"revenue_ttm", "shares_outstanding"}.issubset(f.columns):
            f["_sales_ps_derived"] = pd.to_numeric(f["revenue_ttm"], errors="coerce") / pd.to_numeric(f["shares_outstanding"], errors="coerce")
            denominator = "_sales_ps_derived"
        else:
            raise ValueError("PS percentile requires revenue_per_share_ttm or revenue_ttm + shares_outstanding")
        method = "close / most recent prior TTM revenue per share"
    else:
        raise ValueError("metric must be pe_ttm, pb, or ps_ttm")

    joined = pd.merge_asof(
        p[["date", "close"]], f[["date", denominator]], on="date", direction="backward"
    )
    denom = pd.to_numeric(joined[denominator], errors="coerce")
    joined["denominator"] = denom
    joined["multiple"] = np.where(denom > 0, joined["close"] / denom, np.nan)
    joined["symbol"] = str(symbol)
    joined["metric"] = metric
    joined["method"] = method
    return joined[["symbol", "date", "close", "denominator", "multiple", "metric", "method"]]


def percentile_of_latest(series: pd.DataFrame, *, metric_name: str, lookback_years: float = 5.0) -> dict[str, Any]:
    clean = series.dropna(subset=["multiple"]).copy()
    if clean.empty:
        return {
            "kind": "percentile", "schema_version": "0.3.0", "metric": metric_name,
            "percentile": None, "not_meaningful": True,
            "caveat": "No valid observations; the denominator may be non-positive or unavailable throughout.",
        }
    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    clean = clean.dropna(subset=["date"]).sort_values("date")
    end = clean["date"].max()
    start = end - pd.Timedelta(days=int(lookback_years * 365.25))
    window = clean[clean["date"] >= start]
    if window.empty:
        window = clean.tail(1)
    values = window["multiple"].to_numpy(dtype=float)
    latest = float(values[-1])
    percentile = float((values <= latest).sum() / len(values) * 100.0)
    actual = round((end - window["date"].min()).days / 365.25, 2)
    payload: dict[str, Any] = {
        "kind": "percentile", "schema_version": "0.3.0", "symbol": str(window["symbol"].iloc[-1]) if "symbol" in window else None,
        "metric": metric_name, "method": str(window["method"].iloc[-1]) if "method" in window else None,
        "latest": latest, "percentile": round(percentile, 1), "observations": int(len(values)),
        "window_start": window["date"].min().date().isoformat(), "window_end": end.date().isoformat(),
        "lookback_years_requested": lookback_years, "lookback_years_actual": actual,
        "min": float(np.min(values)), "p25": float(np.percentile(values, 25)),
        "median": float(np.median(values)), "p75": float(np.percentile(values, 75)), "max": float(np.max(values)),
        "not_meaningful": False, "caveat": LOOKAHEAD_CAVEAT,
    }
    if len(values) < MIN_OBSERVATIONS:
        payload["not_meaningful"] = True
        payload["caveat"] = f"Only {len(values)} valid observations (minimum {MIN_OBSERVATIONS}); percentile is unreliable. {LOOKAHEAD_CAVEAT}"
    if actual < lookback_years * 0.8:
        payload["coverage_warning"] = f"History covers {actual}y of the requested {lookback_years}y; the percentile describes a shorter period."
    return payload
