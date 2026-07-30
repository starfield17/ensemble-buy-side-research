from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from ...models import DataError, SourceRecord
from .common import as_float, failed_source

PROVIDER = "yfinance"


def _import_yfinance():
    try:
        import yfinance as yf
    except Exception as exc:  # pragma: no cover - depends on optional package
        return None, exc
    return yf, None


def fetch_prices(symbols: list[str], start: str | None = None, end: str | None = None) -> tuple[pd.DataFrame, list[SourceRecord]]:
    yf, exc = _import_yfinance()
    if yf is None:
        return pd.DataFrame(), [failed_source(PROVIDER, "prices", f"yfinance unavailable: {exc}", missing=["yfinance"], exc=exc)]
    start = start or (date.today() - timedelta(days=365)).isoformat()
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    for symbol in symbols:
        try:
            frame = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=True, actions=False)
            if frame is None or frame.empty:
                records.append(SourceRecord(provider=PROVIDER, dataset="prices", symbol=symbol, status="partial", notes=["No price rows returned."]))
                continue
            local_rows = []
            for timestamp, row in frame.iterrows():
                local_rows.append(
                    {
                        "symbol": symbol,
                        "date": pd.Timestamp(timestamp).date().isoformat(),
                        "open": as_float(row.get("Open")),
                        "high": as_float(row.get("High")),
                        "low": as_float(row.get("Low")),
                        "close": as_float(row.get("Close")),
                        "volume": as_float(row.get("Volume")),
                        "currency": None,
                        "provider": PROVIDER,
                        "adjustment": "auto_adjusted",
                    }
                )
            rows.extend(local_rows)
            records.append(SourceRecord(provider=PROVIDER, dataset="prices", symbol=symbol, status="success", record_count=len(local_rows)))
        except Exception as err:
            records.append(failed_source(PROVIDER, "prices", str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records


def _growth_estimate(obj) -> float | None:
    try:
        estimates = obj.growth_estimates
        if estimates is None or estimates.empty:
            return None
        for index in ("+5y", "+3y", "+1y"):
            if index in estimates.index:
                row = estimates.loc[index]
                value = row.get("stock") if hasattr(row, "get") else None
                parsed = as_float(value)
                if parsed is not None:
                    return parsed
    except Exception:
        return None
    return None


def fetch_fundamentals(symbols: list[str]) -> tuple[pd.DataFrame, list[SourceRecord]]:
    yf, exc = _import_yfinance()
    if yf is None:
        return pd.DataFrame(), [failed_source(PROVIDER, "fundamentals", f"yfinance unavailable: {exc}", missing=["yfinance"], exc=exc)]
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    for symbol in symbols:
        try:
            obj = yf.Ticker(symbol)
            info = obj.info or {}
            shares = as_float(info.get("sharesOutstanding"))
            book_value_per_share = as_float(info.get("bookValue"))
            book_value = book_value_per_share * shares if book_value_per_share is not None and shares is not None else None
            operating_cash_flow = as_float(info.get("operatingCashflow"))
            free_cash_flow = as_float(info.get("freeCashflow"))
            capex = operating_cash_flow - free_cash_flow if operating_cash_flow is not None and free_cash_flow is not None else None
            growth = _growth_estimate(obj)
            row = {
                "symbol": symbol,
                "company": info.get("shortName") or info.get("longName") or symbol,
                "as_of": date.today().isoformat(),
                "currency": info.get("financialCurrency") or info.get("currency"),
                "price": as_float(info.get("currentPrice") or info.get("regularMarketPrice")),
                "shares_outstanding": shares,
                "market_cap": as_float(info.get("marketCap")),
                "enterprise_value": as_float(info.get("enterpriseValue")),
                "revenue_ttm": as_float(info.get("totalRevenue")),
                "net_income_ttm": as_float(info.get("netIncomeToCommon")),
                "book_value": book_value,
                "ebitda_ttm": as_float(info.get("ebitda")),
                "gross_profit_ttm": as_float(info.get("grossProfits")),
                "operating_income_ttm": as_float(info.get("operatingIncome")),
                "operating_cash_flow_ttm": operating_cash_flow,
                "capex_ttm": capex,
                "free_cash_flow_ttm": free_cash_flow,
                "total_debt": as_float(info.get("totalDebt")),
                "cash": as_float(info.get("totalCash")),
                "eps_ttm": as_float(info.get("trailingEps")),
                "forward_eps": as_float(info.get("forwardEps")),
                "eps_growth_3y_cagr": None,
                "eps_growth_5y_cagr": None,
                "analyst_eps_growth_5y": growth,
                "provider": PROVIDER,
            }
            rows.append(row)
            non_null = sum(value is not None for key, value in row.items() if key not in {"symbol", "company", "as_of", "provider"})
            status = "success" if non_null >= 8 else "partial"
            notes = [] if status == "success" else ["Provider returned a sparse fundamentals snapshot."]
            records.append(SourceRecord(provider=PROVIDER, dataset="fundamentals", symbol=symbol, status=status, record_count=1, notes=notes))
        except Exception as err:
            records.append(failed_source(PROVIDER, "fundamentals", str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records


def fetch_etf_snapshot(symbols: list[str]) -> tuple[pd.DataFrame, list[SourceRecord]]:
    yf, exc = _import_yfinance()
    if yf is None:
        return pd.DataFrame(), [failed_source(PROVIDER, "etf", f"yfinance unavailable: {exc}", missing=["yfinance"], exc=exc)]
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    for symbol in symbols:
        try:
            info = yf.Ticker(symbol).info or {}
            row = {
                "symbol": symbol,
                "name": info.get("shortName") or info.get("longName") or symbol,
                "as_of": date.today().isoformat(),
                "timestamp": None,
                "currency": info.get("currency"),
                "market_price": as_float(info.get("currentPrice") or info.get("regularMarketPrice")),
                "iopv": None,
                "nav": as_float(info.get("navPrice")),
                "provider_reported_premium_pct": None,
                "provider": PROVIDER,
            }
            rows.append(row)
            status = "success" if row["market_price"] is not None and row["nav"] is not None else "partial"
            notes = [] if status == "success" else ["Yahoo did not provide both market price and NAV; IOPV is not available from this connector."]
            records.append(SourceRecord(provider=PROVIDER, dataset="etf", symbol=symbol, status=status, record_count=1, notes=notes))
        except Exception as err:
            records.append(failed_source(PROVIDER, "etf", str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records
