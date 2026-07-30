from __future__ import annotations

import math
from typing import Any

import pandas as pd


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def first_number(row: pd.Series, *names: str) -> tuple[float | None, str | None]:
    for name in names:
        if name in row.index:
            value = number(row.get(name))
            if value is not None:
                return value, name
    return None, None


def growth_percentage_points(value: Any) -> float | None:
    result = number(value)
    if result is None:
        return None
    return result * 100.0 if abs(result) <= 1.0 else result


def metadata(row: pd.Series, source_dataset: str) -> dict[str, Any]:
    provider = row.get("provider") or row.get("source")
    return {
        "as_of": str(row.get("as_of") or row.get("date")) if (row.get("as_of") is not None or row.get("date") is not None) else None,
        "fiscal_window": row.get("fiscal_window") or row.get("window"),
        "currency": row.get("currency"),
        "provider": str(provider) if provider is not None else None,
        "source_dataset": source_dataset,
        "adjustment_policy": row.get("adjustment") or row.get("adjustment_policy"),
    }
