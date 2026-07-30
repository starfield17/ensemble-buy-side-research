"""Objective company-level valuation and accounting ratios.

No function in this module scores or ranks a security. A non-positive economic denominator is
reported as not meaningful rather than returned as a negative multiple.
"""
from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from ...models import MetricRecord
from .helpers import growth_percentage_points, metadata, number

CROSS_MARKET_CAVEAT = (
    "Cross-market comparison: accounting standards, currencies, free float, fiscal calendars, "
    "and index inclusion differ; do not average these observations without adjustment."
)


def _record(
    row: pd.Series,
    name: str,
    value: float | None,
    *,
    unit: str,
    method: str,
    formula: str,
    inputs: dict[str, Any],
    caveats: list[str] | None = None,
    not_meaningful: bool = False,
    status: str | None = None,
    cross_market: bool = False,
) -> MetricRecord:
    notes = list(caveats or [])
    if cross_market:
        notes.append(CROSS_MARKET_CAVEAT)
    resolved = status or ("valid" if value is not None and not not_meaningful else "unavailable")
    return MetricRecord(
        symbol=str(row.get("symbol") or row.get("ticker") or "UNKNOWN"),
        metric=name,
        value=value,
        unit=unit,
        method=method,
        formula=formula,
        inputs=inputs,
        status=resolved,
        not_meaningful=not_meaningful,
        caveats=notes,
        **metadata(row, "fundamentals"),
    )


def _ratio(
    row: pd.Series,
    name: str,
    numerator: float | None,
    denominator: float | None,
    *,
    unit: str,
    method: str,
    formula: str,
    inputs: dict[str, Any],
    positive_denominator: bool = True,
    reason: str = "denominator is zero or negative",
    multiplier: float = 1.0,
    cross_market: bool = False,
) -> MetricRecord:
    if numerator is None or denominator is None:
        return _record(
            row, name, None, unit=unit, method=method, formula=formula, inputs=inputs,
            caveats=["Required input is missing."], status="unavailable", cross_market=cross_market,
        )
    if denominator == 0 or (positive_denominator and denominator < 0):
        return _record(
            row, name, None, unit=unit, method=method, formula=formula, inputs=inputs,
            caveats=[reason], not_meaningful=True, status="unavailable", cross_market=cross_market,
        )
    return _record(
        row, name, numerator / denominator * multiplier, unit=unit, method=method,
        formula=formula, inputs=inputs, cross_market=cross_market,
    )


def _market_cap(row: pd.Series) -> tuple[float | None, str]:
    direct = number(row.get("market_cap"))
    if direct is not None:
        return direct, "provider-reported market capitalization"
    price = number(row.get("price")) or number(row.get("close"))
    shares = number(row.get("shares_diluted")) or number(row.get("shares_outstanding")) or number(row.get("shares"))
    if price is None or shares is None:
        return None, "market capitalization unavailable"
    return price * shares, "price × shares outstanding"


def _enterprise_value(row: pd.Series, market_cap: float | None) -> tuple[float | None, str, dict[str, Any], list[str]]:
    reported = number(row.get("enterprise_value"))
    if reported is not None:
        return reported, "provider-reported enterprise value", {"enterprise_value": reported}, []
    if market_cap is None:
        return None, "enterprise value unavailable", {}, ["Market capitalization is unavailable."]
    debt = number(row.get("total_debt"))
    cash = number(row.get("cash_and_equivalents"))
    if cash is None:
        cash = number(row.get("cash"))
    minority = number(row.get("minority_interest"))
    caveats: list[str] = []
    if debt is None:
        debt = 0.0
        caveats.append("Total debt unavailable and treated as zero; EV may be understated.")
    if cash is None:
        cash = 0.0
        caveats.append("Cash unavailable and treated as zero; EV may be overstated.")
    if minority is None:
        minority = 0.0
        caveats.append("Minority interest unavailable and treated as zero.")
    ev = market_cap + debt + minority - cash
    return (
        ev,
        "market cap + total debt + minority interest - cash",
        {"market_cap": market_cap, "total_debt": debt, "minority_interest": minority, "cash": cash},
        caveats,
    )


def calculate_fundamental_metrics(
    frame: pd.DataFrame,
    *,
    custom_growth_rates: Mapping[str, float] | None = None,
    cross_market: bool = False,
) -> list[MetricRecord]:
    """Calculate objective metrics for the latest row of each symbol.

    `custom_growth_rates` uses decimal rates (0.18 means 18%) and creates `peg_custom`. It is never
    inferred from another column, because selecting a growth horizon is an analytical decision.
    """
    if frame.empty:
        return []
    work = frame.copy()
    if "as_of" in work.columns:
        work["_as_of_sort"] = pd.to_datetime(work["as_of"], errors="coerce")
        work = work.sort_values(["symbol", "_as_of_sort"], na_position="first").drop_duplicates("symbol", keep="last")
    elif "symbol" in work.columns:
        work = work.drop_duplicates("symbol", keep="last")

    custom_growth_rates = custom_growth_rates or {}
    records: list[MetricRecord] = []
    for _, row in work.iterrows():
        symbol = str(row.get("symbol") or row.get("ticker") or "UNKNOWN")
        price = number(row.get("price")) or number(row.get("close"))
        shares = number(row.get("shares_outstanding")) or number(row.get("shares_diluted"))
        market_cap, cap_method = _market_cap(row)
        revenue = number(row.get("revenue_ttm"))
        net_income = number(row.get("net_income_ttm"))
        book = number(row.get("book_value"))
        eps = number(row.get("eps_ttm_diluted")) or number(row.get("eps_ttm"))
        eps_ex = number(row.get("eps_ttm_ex_items")) or number(row.get("eps_ttm_recurring"))
        eps_static = number(row.get("eps_last_fy")) or number(row.get("eps_fy"))
        forward_eps = number(row.get("forward_eps"))
        bvps = number(row.get("book_value_per_share")) or number(row.get("bvps"))
        if bvps is None and book is not None and shares is not None and shares > 0:
            bvps = book / shares

        if market_cap is not None and net_income is not None:
            pe = _ratio(
                row, "pe_ttm", market_cap, net_income, unit="x",
                method=f"{cap_method} / TTM net income",
                formula="market_cap / net_income_ttm",
                inputs={"market_cap": market_cap, "net_income_ttm": net_income},
                reason="TTM earnings are zero or negative; no meaningful PE.", cross_market=cross_market,
            )
        else:
            pe = _ratio(
                row, "pe_ttm", price, eps, unit="x", method="price / diluted TTM EPS",
                formula="price / eps_ttm_diluted",
                inputs={"price": price, "eps_ttm_diluted": eps},
                reason="TTM EPS is zero or negative; no meaningful PE.", cross_market=cross_market,
            )
        records.append(pe)
        records.append(_ratio(
            row, "pe_ttm_ex_items", price, eps_ex, unit="x",
            method="price / diluted TTM EPS excluding non-recurring items",
            formula="price / eps_ttm_ex_items", inputs={"price": price, "eps_ttm_ex_items": eps_ex},
            reason="Recurring TTM EPS is zero or negative; no meaningful PE.", cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "pe_static", price, eps_static, unit="x", method="price / last full-year diluted EPS",
            formula="price / eps_last_fy", inputs={"price": price, "eps_last_fy": eps_static},
            reason="Last full-year EPS is zero or negative; no meaningful PE.", cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "pe_forward", price, forward_eps, unit="x", method="price / forward consensus EPS",
            formula="price / forward_eps", inputs={"price": price, "forward_eps": forward_eps},
            reason="Forward EPS is zero or negative; no meaningful forward PE.", cross_market=cross_market,
        ))

        if market_cap is not None and book is not None:
            records.append(_ratio(
                row, "pb", market_cap, book, unit="x", method=f"{cap_method} / common equity book value",
                formula="market_cap / book_value", inputs={"market_cap": market_cap, "book_value": book},
                reason="Book value is zero or negative; PB is not meaningful.", cross_market=cross_market,
            ))
        else:
            records.append(_ratio(
                row, "pb", price, bvps, unit="x", method="price / book value per share",
                formula="price / book_value_per_share", inputs={"price": price, "book_value_per_share": bvps},
                reason="Book value per share is zero or negative; PB is not meaningful.", cross_market=cross_market,
            ))
        records.append(_ratio(
            row, "ps_ttm", market_cap, revenue, unit="x", method=f"{cap_method} / TTM revenue",
            formula="market_cap / revenue_ttm", inputs={"market_cap": market_cap, "revenue_ttm": revenue},
            reason="TTM revenue is zero or negative; PS is not meaningful.", cross_market=cross_market,
        ))

        ev, ev_method, ev_inputs, ev_caveats = _enterprise_value(row, market_cap)
        ev_record = _ratio(
            row, "ev_ebitda", ev, number(row.get("ebitda_ttm")), unit="x",
            method=f"EV / TTM EBITDA; EV = {ev_method}", formula="enterprise_value / ebitda_ttm",
            inputs={**ev_inputs, "ebitda_ttm": number(row.get("ebitda_ttm"))},
            reason="TTM EBITDA is zero or negative; EV/EBITDA is not meaningful.", cross_market=cross_market,
        )
        ev_record.caveats = ev_caveats + ev_record.caveats
        records.append(ev_record)

        ocf = number(row.get("operating_cash_flow_ttm"))
        capex = number(row.get("capex_ttm"))
        fcf = number(row.get("free_cash_flow_ttm"))
        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf - capex
        records.append(_ratio(
            row, "fcf_yield", fcf, market_cap, unit="%", method="TTM free cash flow / market capitalization",
            formula="free_cash_flow_ttm / market_cap * 100",
            inputs={"free_cash_flow_ttm": fcf, "market_cap": market_cap},
            reason="Market capitalization is zero or negative.", multiplier=100.0, cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "roe", net_income, book, unit="%", method="TTM net income / common equity book value",
            formula="net_income_ttm / book_value * 100", inputs={"net_income_ttm": net_income, "book_value": book},
            reason="Book value is zero or negative; ROE is not meaningful.", multiplier=100.0, cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "debt_to_equity", number(row.get("total_debt")), book, unit="x",
            method="interest-bearing total debt / common equity book value",
            formula="total_debt / book_value", inputs={"total_debt": number(row.get("total_debt")), "book_value": book},
            reason="Book value is zero or negative; debt/equity is not meaningful.", cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "gross_margin", number(row.get("gross_profit_ttm")), revenue, unit="%",
            method="TTM gross profit / TTM revenue", formula="gross_profit_ttm / revenue_ttm * 100",
            inputs={"gross_profit_ttm": number(row.get("gross_profit_ttm")), "revenue_ttm": revenue},
            reason="TTM revenue is zero or negative.", multiplier=100.0, cross_market=cross_market,
        ))
        records.append(_ratio(
            row, "operating_margin", number(row.get("operating_income_ttm")), revenue, unit="%",
            method="TTM operating income / TTM revenue", formula="operating_income_ttm / revenue_ttm * 100",
            inputs={"operating_income_ttm": number(row.get("operating_income_ttm")), "revenue_ttm": revenue},
            reason="TTM revenue is zero or negative.", multiplier=100.0, cross_market=cross_market,
        ))

        for metric_name, column, method in (
            ("peg_historical_3y", "eps_growth_3y_cagr", "PE(TTM) / 3-year historical EPS CAGR in percentage points"),
            ("peg_historical_5y", "eps_growth_5y_cagr", "PE(TTM) / 5-year historical EPS CAGR in percentage points"),
            ("peg_forward_consensus", "analyst_eps_growth_5y", "PE(TTM) / consensus 5-year EPS growth in percentage points"),
        ):
            growth = growth_percentage_points(row.get(column))
            peg = None
            notes: list[str] = []
            not_meaningful = False
            if pe.value is None:
                notes.append(f"PE unavailable: {'; '.join(pe.caveats) or 'missing inputs'}")
            elif growth is None:
                notes.append("Growth input is missing.")
            elif growth <= 0:
                notes.append("Growth rate is zero or negative; PEG is not meaningful.")
                not_meaningful = True
            else:
                peg = pe.value / growth
            records.append(_record(
                row, metric_name, peg, unit="x", method=method, formula=f"pe_ttm / {column}_percentage_points",
                inputs={"pe_ttm": pe.value, f"{column}_percentage_points": growth}, caveats=notes,
                not_meaningful=not_meaningful, cross_market=cross_market,
            ))

        if symbol in custom_growth_rates:
            raw_growth = custom_growth_rates[symbol]
            growth_pp = growth_percentage_points(raw_growth)
            peg = pe.value / growth_pp if pe.value is not None and growth_pp is not None and growth_pp > 0 else None
            notes = ["Analyst-supplied growth assumption; cite its source and horizon in the memo."]
            nm = False
            if growth_pp is None or growth_pp <= 0:
                notes.append("Custom growth is zero, negative, or invalid; PEG is not meaningful.")
                nm = True
            if pe.value is None:
                notes.append("PE is unavailable.")
            records.append(_record(
                row, "peg_custom", peg, unit="x",
                method="PE(TTM) / analyst-supplied annual growth in percentage points",
                formula="pe_ttm / custom_growth_percentage_points",
                inputs={"pe_ttm": pe.value, "custom_growth_percentage_points": growth_pp},
                caveats=notes, not_meaningful=nm, cross_market=cross_market,
            ))
    return records
