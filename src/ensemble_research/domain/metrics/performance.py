from __future__ import annotations

import math

import pandas as pd

from ...models import MetricRecord


def calculate_performance_metrics(frame: pd.DataFrame) -> list[MetricRecord]:
    if frame.empty or not {"symbol", "date", "close"}.issubset(frame.columns):
        return []
    work = frame.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work["close"] = pd.to_numeric(work["close"], errors="coerce")
    work = work.dropna(subset=["date", "close"])
    records: list[MetricRecord] = []
    for symbol, group in work.groupby("symbol"):
        group = group.sort_values("date").drop_duplicates("date", keep="last")
        if group.empty:
            continue
        close = group["close"]
        returns = close.pct_change().dropna()
        first = float(close.iloc[0])
        last = float(close.iloc[-1])
        total_return = (last / first - 1.0) * 100.0 if len(close) >= 2 and first > 0 else None
        volatility = float(returns.std(ddof=1) * math.sqrt(252) * 100.0) if len(returns) >= 2 else None
        drawdown = close / close.cummax() - 1.0
        max_drawdown = float(drawdown.min() * 100.0) if not drawdown.empty else None
        provider_values = group["provider"].dropna().astype(str).unique().tolist() if "provider" in group else []
        provider = provider_values[0] if len(provider_values) == 1 else ("mixed" if provider_values else None)
        adjustments = group["adjustment"].dropna().astype(str).unique().tolist() if "adjustment" in group else []
        adjustment = adjustments[0] if len(adjustments) == 1 else ("mixed" if adjustments else None)
        as_of = group["date"].iloc[-1].date().isoformat()
        currency = str(group["currency"].dropna().iloc[-1]) if "currency" in group and group["currency"].notna().any() else None
        base = dict(symbol=str(symbol), as_of=as_of, currency=currency, provider=provider, source_dataset="prices", adjustment_policy=adjustment)
        specs = (
            ("period_return", total_return, "%", "total return over supplied price window", "(last_close / first_close - 1) * 100", {"first_close": first, "last_close": last, "observations": len(close)}),
            ("annualized_volatility", volatility, "%", "sample standard deviation of daily returns annualized with 252 sessions", "std(daily_returns, ddof=1) * sqrt(252) * 100", {"return_observations": len(returns), "annualization_sessions": 252}),
            ("max_drawdown", max_drawdown, "%", "minimum decline from prior running peak over supplied window", "min(close / cumulative_max(close) - 1) * 100", {"observations": len(close)}),
        )
        for metric, value, unit, method, formula, inputs in specs:
            records.append(MetricRecord(
                metric=metric, value=value, unit=unit, method=method, formula=formula, inputs=inputs,
                status="valid" if value is not None else "unavailable", not_meaningful=False,
                caveats=[] if value is not None else ["Insufficient valid price observations."], **base,
            ))
    return records
