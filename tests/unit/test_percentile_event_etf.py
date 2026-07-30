from __future__ import annotations

import pandas as pd

from ensemble_research.domain.metrics.etf import calculate_etf_metrics
from ensemble_research.domain.metrics.event_study import run_event_study
from ensemble_research.domain.metrics.percentile import build_multiple_series, percentile_of_latest


def test_etf_premium_percentage_points_and_iopv_caveat():
    frame = pd.DataFrame([{"symbol": "ETF", "as_of": "2026-01-01", "market_price": 1.05, "iopv": 1.0, "nav": 1.02, "provider": "fixture"}])
    records = calculate_etf_metrics(frame)
    iopv = next(r for r in records if r.metric == "premium_to_iopv")
    assert round(iopv.value, 8) == 5.0
    assert any("intraday estimate" in c for c in iopv.caveats)


def test_percentile_window_and_short_history_flag():
    dates = pd.bdate_range("2022-01-03", periods=800)
    prices = pd.DataFrame({"symbol": "AAA", "date": dates, "close": [100 + i * 0.05 for i in range(len(dates))]})
    fundamentals = pd.DataFrame({"symbol": ["AAA"], "as_of": ["2021-12-31"], "eps_ttm_diluted": [4.0]})
    series = build_multiple_series(prices, fundamentals, symbol="AAA", metric="pe_ttm")
    result = percentile_of_latest(series, metric_name="pe_ttm", lookback_years=3)
    assert result["percentile"] == 100.0 and result["observations"] >= 60
    short = percentile_of_latest(series.head(20), metric_name="pe_ttm", lookback_years=5)
    assert short["not_meaningful"] and "minimum" in short["caveat"]


def _prices():
    dates = pd.bdate_range("2026-01-01", periods=120)
    rows = []
    for i, day in enumerate(dates):
        rows.append({"symbol": "AAA", "date": day, "close": 100 * (1.001 ** i)})
        rows.append({"symbol": "SPY", "date": day, "close": 400 * (1.001 ** i)})
    frame = pd.DataFrame(rows)
    event_day = dates[60]
    frame.loc[(frame.symbol == "AAA") & (frame.date >= event_day), "close"] *= 1.10
    return frame, dates


def test_market_adjustment_and_weekend_anchor():
    prices, dates = _prices()
    result = run_event_study([{"id": "e1", "date": dates[60], "symbols": ["AAA"]}], prices, benchmark="SPY", model="market-adjusted")
    row = result[result.window == "[0,5] trading days"].iloc[0]
    assert abs(row.abnormal_return_pct - 10.0) < 0.5
    weekend = run_event_study([{"id": "e2", "date": "2026-02-07", "symbols": ["AAA"]}], prices, benchmark="SPY")
    assert "not a trading session" in weekend.iloc[0].note


def test_raw_mode_is_not_labelled_abnormal():
    prices, dates = _prices()
    result = run_event_study([{"date": dates[60], "symbols": ["AAA"]}], prices, benchmark=None)
    assert (result.model == "raw").all()
    assert result.abnormal_return_pct.isna().all()
    assert "not abnormal" in result.note.iloc[0]


def test_market_model_falls_back_with_short_estimation_window():
    prices, dates = _prices()
    result = run_event_study([{"date": dates[40], "symbols": ["AAA"]}], prices, benchmark="SPY", model="market-model")
    assert (result.model == "market_adjusted").all()
    assert "fell back" in result.note.iloc[0]
