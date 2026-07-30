from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from ...models import SourceRecord
from ...security import bare_cn_symbol
from .common import as_float, failed_source

PROVIDER = "akshare"


def _import_akshare():
    try:
        import akshare as ak
    except Exception as exc:  # pragma: no cover
        return None, exc
    return ak, None


def _pick(row: pd.Series, *names: str):
    for name in names:
        if name in row.index and pd.notna(row[name]):
            return row[name]
    return None


def fetch_prices(symbols: list[str], start: str | None = None, end: str | None = None, *, etf: bool = False) -> tuple[pd.DataFrame, list[SourceRecord]]:
    ak, exc = _import_akshare()
    dataset = "etf_prices" if etf else "prices"
    if ak is None:
        return pd.DataFrame(), [failed_source(PROVIDER, dataset, f"akshare unavailable: {exc}", missing=["akshare"], exc=exc)]
    start = (start or (date.today() - timedelta(days=365)).isoformat()).replace("-", "")
    end = (end or date.today().isoformat()).replace("-", "")
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    for symbol in symbols:
        code = bare_cn_symbol(symbol)
        try:
            if etf:
                frame = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
            else:
                frame = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
            if frame is None or frame.empty:
                records.append(SourceRecord(provider=PROVIDER, dataset=dataset, symbol=symbol, status="partial", notes=["No rows returned."]))
                continue
            local_rows = []
            for _, row in frame.iterrows():
                local_rows.append(
                    {
                        "symbol": symbol,
                        "date": str(_pick(row, "日期", "date"))[:10],
                        "open": as_float(_pick(row, "开盘", "open")),
                        "high": as_float(_pick(row, "最高", "high")),
                        "low": as_float(_pick(row, "最低", "low")),
                        "close": as_float(_pick(row, "收盘", "close")),
                        "volume": as_float(_pick(row, "成交量", "volume")),
                        "currency": "CNY",
                        "provider": PROVIDER,
                        "adjustment": "qfq",
                    }
                )
            rows.extend(local_rows)
            records.append(SourceRecord(provider=PROVIDER, dataset=dataset, symbol=symbol, status="success", record_count=len(local_rows)))
        except Exception as err:
            records.append(failed_source(PROVIDER, dataset, str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records


def fetch_etf_snapshot(symbols: list[str]) -> tuple[pd.DataFrame, list[SourceRecord]]:
    ak, exc = _import_akshare()
    if ak is None:
        return pd.DataFrame(), [failed_source(PROVIDER, "etf", f"akshare unavailable: {exc}", missing=["akshare"], exc=exc)]
    try:
        frame = ak.fund_etf_spot_em()
    except Exception as err:
        return pd.DataFrame(), [failed_source(PROVIDER, "etf", str(err), exc=err)]
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    code_column = next((name for name in ("代码", "基金代码", "symbol") if name in frame.columns), None)
    if code_column is None:
        return pd.DataFrame(), [failed_source(PROVIDER, "etf", "ETF snapshot has no recognizable code column.")]
    wanted = {bare_cn_symbol(symbol): symbol for symbol in symbols}
    for _, row in frame.iterrows():
        code = str(row.get(code_column, "")).strip()
        if code not in wanted:
            continue
        symbol = wanted[code]
        result = {
            "symbol": symbol,
            "name": _pick(row, "名称", "基金简称", "name") or symbol,
            "as_of": date.today().isoformat(),
            "timestamp": None,
            "currency": "CNY",
            "market_price": as_float(_pick(row, "最新价", "现价", "price")),
            "iopv": as_float(_pick(row, "IOPV实时估值", "IOPV", "iopv")),
            "nav": as_float(_pick(row, "单位净值", "基金净值", "nav")),
            "provider_reported_premium_pct": as_float(_pick(row, "基金折价率", "溢价率", "折溢价率")),
            "provider": PROVIDER,
        }
        rows.append(result)
        records.append(SourceRecord(provider=PROVIDER, dataset="etf", symbol=symbol, status="success", record_count=1))
    missing = [symbol for code, symbol in wanted.items() if not any(row["symbol"] == symbol for row in rows)]
    for symbol in missing:
        records.append(SourceRecord(provider=PROVIDER, dataset="etf", symbol=symbol, status="partial", notes=["Symbol not present in AKShare ETF snapshot."]))
    return pd.DataFrame(rows), records
