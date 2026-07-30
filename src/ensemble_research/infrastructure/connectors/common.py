from __future__ import annotations

from typing import Any

import pandas as pd

from ...models import DataError, SourceRecord


def as_float(value: Any) -> float | None:
    if value is None or value is pd.NA:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(result):
        return None
    return result


def failed_source(provider: str, dataset: str, message: str, *, symbol: str | None = None, missing: list[str] | None = None, exc: Exception | None = None) -> SourceRecord:
    return SourceRecord(
        provider=provider,
        dataset=dataset,
        symbol=symbol,
        status="failed",
        errors=[
            DataError(
                module=f"{provider}.{dataset}",
                item=symbol,
                message=message,
                missing_inputs=missing or [],
                exception_type=type(exc).__name__ if exc else None,
            )
        ],
    )
