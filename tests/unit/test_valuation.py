from __future__ import annotations

import pandas as pd

from ensemble_research.domain.metrics.valuation import calculate_fundamental_metrics


def get(records, metric):
    return next(record for record in records if record.metric == metric)


def base(**overrides):
    row = {
        "symbol": "AAA", "as_of": "2026-06-30", "currency": "USD", "provider": "fixture",
        "price": 100.0, "shares_outstanding": 10.0, "market_cap": 1000.0,
        "revenue_ttm": 500.0, "net_income_ttm": 40.0, "book_value": 250.0,
        "ebitda_ttm": 80.0, "gross_profit_ttm": 300.0, "operating_income_ttm": 100.0,
        "free_cash_flow_ttm": 50.0, "total_debt": 120.0, "cash": 30.0,
        "minority_interest": 10.0, "eps_ttm_diluted": 4.0, "eps_ttm_ex_items": 3.5,
        "eps_last_fy": 3.0, "book_value_per_share": 25.0, "forward_eps": 5.0,
        "eps_growth_3y_cagr": 0.20, "eps_growth_5y_cagr": 0.15, "analyst_eps_growth_5y": 0.12,
    }
    row.update(overrides)
    return row


def test_objective_values_and_provenance():
    records = calculate_fundamental_metrics(pd.DataFrame([base()]))
    assert get(records, "pe_ttm").value == 25.0
    assert get(records, "pb").value == 4.0
    assert get(records, "ps_ttm").value == 2.0
    assert get(records, "ev_ebitda").value == (1000 + 120 + 10 - 30) / 80
    pe = get(records, "pe_ttm")
    assert pe.provider == "fixture" and pe.currency == "USD"
    assert pe.inputs == {"market_cap": 1000.0, "net_income_ttm": 40.0}


def test_nonpositive_earnings_do_not_emit_negative_pe():
    records = calculate_fundamental_metrics(pd.DataFrame([base(net_income_ttm=-40.0, eps_ttm_diluted=-4.0)]))
    pe = get(records, "pe_ttm")
    assert pe.value is None and pe.not_meaningful and pe.status == "unavailable"


def test_nonpositive_book_value_blocks_pb_and_roe():
    records = calculate_fundamental_metrics(pd.DataFrame([base(book_value=-1.0, book_value_per_share=-0.1)]))
    assert get(records, "pb").not_meaningful
    assert get(records, "roe").not_meaningful


def test_missing_minority_interest_is_disclosed():
    records = calculate_fundamental_metrics(pd.DataFrame([base(enterprise_value=None, minority_interest=None)]))
    metric = get(records, "ev_ebitda")
    assert any("Minority interest unavailable" in note for note in metric.caveats)


def test_custom_peg_requires_explicit_growth():
    no_custom = calculate_fundamental_metrics(pd.DataFrame([base()]))
    assert not any(record.metric == "peg_custom" for record in no_custom)
    custom = calculate_fundamental_metrics(pd.DataFrame([base()]), custom_growth_rates={"AAA": 0.25})
    assert get(custom, "peg_custom").value == 1.0
    assert "Analyst-supplied" in get(custom, "peg_custom").caveats[0]


def test_latest_fundamental_row_is_selected_per_symbol():
    old = base(as_of="2025-12-31", net_income_ttm=20.0)
    new = base(as_of="2026-06-30", net_income_ttm=50.0)
    records = calculate_fundamental_metrics(pd.DataFrame([new, old]))
    assert get(records, "pe_ttm").value == 20.0


def test_cross_market_caveat_propagates():
    records = calculate_fundamental_metrics(pd.DataFrame([base()]), cross_market=True)
    assert all(any("Cross-market" in caveat for caveat in record.caveats) for record in records)
