from __future__ import annotations

import pandas as pd

from ...models import MetricRecord
from .helpers import metadata, number

CROSS_BORDER_CAVEAT = (
    "Cross-border/QDII fund: underlying markets, FX, quota constraints, and the fund trading session "
    "may be asynchronous; a premium can persist without being immediately arbitrageable."
)


def calculate_etf_metrics(frame: pd.DataFrame) -> list[MetricRecord]:
    records: list[MetricRecord] = []
    for _, row in frame.iterrows():
        price = number(row.get("market_price")) or number(row.get("close"))
        cross_border = bool(row.get("cross_border", False))
        for metric, denominator_name, method in (
            ("premium_to_iopv", "iopv", "(market price - IOPV) / IOPV"),
            ("premium_to_nav", "nav", "(market price - official NAV) / official NAV"),
        ):
            denominator = number(row.get(denominator_name))
            caveats: list[str] = []
            not_meaningful = False
            value = None
            if price is None or denominator is None:
                caveats.append("Market price or comparison value is missing.")
            elif denominator <= 0:
                caveats.append(f"{denominator_name} is zero or negative.")
                not_meaningful = True
            else:
                value = (price / denominator - 1.0) * 100.0
            if denominator_name == "iopv":
                caveats.append("IOPV is an intraday estimate; official NAV is struck separately and may be disclosed later.")
            if cross_border:
                caveats.append(CROSS_BORDER_CAVEAT)
            meta = metadata(row, "etf_snapshot")
            meta["as_of"] = str(row.get("timestamp") or row.get("as_of") or meta.get("as_of"))
            records.append(MetricRecord(
                symbol=str(row.get("symbol") or "UNKNOWN"), metric=metric, value=value, unit="%",
                method=method, formula=f"(market_price / {denominator_name} - 1) * 100",
                inputs={"market_price": price, denominator_name: denominator},
                status="valid" if value is not None else "unavailable", not_meaningful=not_meaningful,
                caveats=caveats, **meta,
            ))
    return records


def premium_series(
    frame: pd.DataFrame,
    *,
    basis: str = "nav",
    price_column: str = "close",
    reference_column: str | None = None,
    cross_border: bool = False,
) -> pd.DataFrame:
    if basis not in {"nav", "iopv"}:
        raise ValueError("basis must be 'nav' or 'iopv'")
    reference_column = reference_column or basis
    missing = [name for name in ("date", price_column, reference_column) if name not in frame.columns]
    if missing:
        raise ValueError(f"missing columns: {missing}")
    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    price = pd.to_numeric(result[price_column], errors="coerce")
    ref = pd.to_numeric(result[reference_column], errors="coerce")
    result["premium_pct"] = (price / ref - 1.0).where(ref > 0) * 100.0
    result["basis"] = basis
    result["method"] = f"(market price - {basis.upper()}) / {basis.upper()}"
    result["caveat"] = CROSS_BORDER_CAVEAT if cross_border else None
    return result.sort_values("date").reset_index(drop=True)
