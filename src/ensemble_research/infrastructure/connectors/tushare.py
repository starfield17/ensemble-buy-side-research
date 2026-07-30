from __future__ import annotations

from datetime import date

import pandas as pd

from ...models import SourceRecord
from ...security import tushare_symbol
from .common import as_float, failed_source

PROVIDER = "tushare"


def _client(token: str | None):
    if not token:
        return None, ValueError("TUSHARE_TOKEN not set")
    try:
        import tushare as ts
    except Exception as exc:  # pragma: no cover
        return None, exc
    try:
        return ts.pro_api(token), None
    except Exception as exc:
        return None, exc


def _clean_reports(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    work = frame.copy()
    if "report_type" in work.columns:
        preferred = work[work["report_type"].astype(str) == "1"]
        if not preferred.empty:
            work = preferred
    work["end_date"] = pd.to_datetime(work["end_date"], errors="coerce")
    work["ann_date"] = pd.to_datetime(work.get("ann_date"), errors="coerce")
    work = work.dropna(subset=["end_date"]).sort_values(["end_date", "ann_date"])
    return work.drop_duplicates("end_date", keep="last")


def _single_quarters(frame: pd.DataFrame, field: str) -> pd.DataFrame:
    """Convert Chinese cumulative YTD statements to discrete quarters."""
    work = _clean_reports(frame)
    if work.empty or field not in work.columns:
        return pd.DataFrame(columns=["end_date", "value"])
    work["value"] = pd.to_numeric(work[field], errors="coerce")
    rows: list[dict[str, object]] = []
    for year, group in work.groupby(work["end_date"].dt.year):
        cumulative = {int(row.end_date.month): row.value for row in group.itertuples() if pd.notna(row.value)}
        if 3 in cumulative:
            rows.append({"end_date": pd.Timestamp(year=year, month=3, day=31), "value": cumulative[3]})
        if 6 in cumulative and 3 in cumulative:
            rows.append({"end_date": pd.Timestamp(year=year, month=6, day=30), "value": cumulative[6] - cumulative[3]})
        if 9 in cumulative and 6 in cumulative:
            rows.append({"end_date": pd.Timestamp(year=year, month=9, day=30), "value": cumulative[9] - cumulative[6]})
        if 12 in cumulative and 9 in cumulative:
            rows.append({"end_date": pd.Timestamp(year=year, month=12, day=31), "value": cumulative[12] - cumulative[9]})
    return pd.DataFrame(rows).sort_values("end_date") if rows else pd.DataFrame(columns=["end_date", "value"])


def _ttm(frame: pd.DataFrame, field: str) -> tuple[float | None, str | None]:
    quarters = _single_quarters(frame, field).dropna(subset=["value"])
    if len(quarters) < 4:
        return None, None
    latest = quarters.tail(4)
    gaps = latest["end_date"].diff().dropna().dt.days
    if len(gaps) and gaps.max() > 100:
        return None, None
    start = latest["end_date"].iloc[0].date().isoformat()
    end = latest["end_date"].iloc[-1].date().isoformat()
    return float(latest["value"].sum()), f"TTM {start} to {end} reconstructed from four discrete quarters"


def _latest(frame: pd.DataFrame) -> pd.Series:
    work = _clean_reports(frame)
    return work.iloc[-1] if not work.empty else pd.Series(dtype=object)


def _sum_debt(balance: pd.Series) -> tuple[float | None, list[str]]:
    fields = ("st_borr", "lt_borr", "bond_payable", "non_cur_liab_due_1y")
    values = [as_float(balance.get(field)) for field in fields]
    present = [value for value in values if value is not None]
    if not present:
        return None, ["Interest-bearing debt fields were unavailable; total liabilities were deliberately not substituted."]
    missing = [field for field, value in zip(fields, values, strict=True) if value is None]
    notes = [f"Debt excludes unavailable components: {', '.join(missing)}."] if missing else []
    return float(sum(present)), notes


def fetch_fundamentals(symbols: list[str], token: str | None) -> tuple[pd.DataFrame, list[SourceRecord]]:
    pro, exc = _client(token)
    if pro is None:
        missing = ["TUSHARE_TOKEN"] if not token else ["tushare"]
        return pd.DataFrame(), [failed_source(PROVIDER, "fundamentals", str(exc), missing=missing, exc=exc)]
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    today = date.today().strftime("%Y%m%d")
    for symbol in symbols:
        ts_code = tushare_symbol(symbol)
        try:
            daily = pro.daily_basic(ts_code=ts_code, end_date=today, fields="ts_code,trade_date,close,total_mv,total_share").head(1)
            income = pro.income(
                ts_code=ts_code,
                fields="ts_code,ann_date,end_date,report_type,total_revenue,oper_cost,n_income_attr_p,ebitda,operate_profit",
            ).head(16)
            balance = pro.balancesheet(
                ts_code=ts_code,
                fields="ts_code,ann_date,end_date,report_type,total_hldr_eqy_exc_min_int,money_cap,st_borr,lt_borr,bond_payable,non_cur_liab_due_1y,minority_int",
            ).head(6)
            cashflow = pro.cashflow(
                ts_code=ts_code,
                fields="ts_code,ann_date,end_date,report_type,n_cashflow_act,c_pay_acq_const_fiolta",
            ).head(16)
            d = daily.iloc[0] if not daily.empty else pd.Series(dtype=object)
            b = _latest(balance)
            market_cap = as_float(d.get("total_mv"))
            if market_cap is not None:
                market_cap *= 10_000.0
            shares = as_float(d.get("total_share"))
            if shares is not None:
                shares *= 10_000.0

            revenue, fiscal_window = _ttm(income, "total_revenue")
            net_income, net_window = _ttm(income, "n_income_attr_p")
            ebitda, ebitda_window = _ttm(income, "ebitda")
            operating_income, op_window = _ttm(income, "operate_profit")
            operating_cost, cost_window = _ttm(income, "oper_cost")
            ocf, ocf_window = _ttm(cashflow, "n_cashflow_act")
            capex, capex_window = _ttm(cashflow, "c_pay_acq_const_fiolta")
            total_debt, debt_notes = _sum_debt(b)
            cash = as_float(b.get("money_cap"))
            minority = as_float(b.get("minority_int"))
            book = as_float(b.get("total_hldr_eqy_exc_min_int"))
            gross_profit = revenue - operating_cost if revenue is not None and operating_cost is not None else None
            fcf = ocf - capex if ocf is not None and capex is not None else None
            eps = net_income / shares if net_income is not None and shares is not None and shares > 0 else None
            enterprise_value = None
            if market_cap is not None and total_debt is not None and cash is not None:
                enterprise_value = market_cap + total_debt + (minority or 0.0) - cash

            windows = [value for value in (fiscal_window, net_window, ebitda_window, op_window, cost_window, ocf_window, capex_window) if value]
            common_window = max(set(windows), key=windows.count) if windows else None
            as_of_raw = d.get("trade_date") or b.get("ann_date") or date.today().isoformat()
            as_of = pd.to_datetime(as_of_raw, errors="coerce")
            as_of_text = as_of.date().isoformat() if pd.notna(as_of) else str(as_of_raw)
            row = {
                "symbol": symbol, "company": symbol, "as_of": as_of_text, "currency": "CNY",
                "fiscal_window": common_window, "price": as_float(d.get("close")),
                "shares_outstanding": shares, "market_cap": market_cap, "enterprise_value": enterprise_value,
                "revenue_ttm": revenue, "net_income_ttm": net_income, "book_value": book,
                "ebitda_ttm": ebitda, "gross_profit_ttm": gross_profit,
                "operating_income_ttm": operating_income, "operating_cash_flow_ttm": ocf,
                "capex_ttm": capex, "free_cash_flow_ttm": fcf, "total_debt": total_debt,
                "cash": cash, "minority_interest": minority, "eps_ttm": eps,
                "eps_ttm_diluted": None, "eps_ttm_ex_items": None, "eps_last_fy": None,
                "forward_eps": None, "eps_growth_3y_cagr": None, "eps_growth_5y_cagr": None,
                "analyst_eps_growth_5y": None, "provider": PROVIDER,
            }
            rows.append(row)
            notes = list(debt_notes)
            if revenue is None or net_income is None:
                notes.append("Four compatible discrete quarters could not be reconstructed; unavailable fields were not labelled TTM.")
            if eps is not None:
                notes.append("EPS was derived as TTM attributable net income / latest shares; it is not provider-reported diluted EPS.")
            status = "success" if market_cap is not None and revenue is not None and net_income is not None and book is not None else "partial"
            records.append(SourceRecord(provider=PROVIDER, dataset="fundamentals", symbol=symbol, status=status, record_count=1, notes=notes))
        except Exception as err:
            records.append(failed_source(PROVIDER, "fundamentals", str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records
