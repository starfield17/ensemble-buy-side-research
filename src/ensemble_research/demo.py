from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import now_utc
from .io import ensure_dir, write_frame, write_json
from .models import RunManifest, SourceRecord


def create_demo_run(run_dir: str | Path) -> RunManifest:
    """Create deterministic synthetic data covering most offline workflows."""
    run_dir = ensure_dir(run_dir)
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=1500)
    price_rows: list[dict[str, object]] = []
    specs = (("ALPHA", 100.0, 0.00055, 0.015), ("BETA", 80.0, 0.00025, 0.017), ("SPY", 250.0, 0.00035, 0.010))
    closes_by_symbol: dict[str, np.ndarray] = {}
    for symbol, start_price, drift, vol in specs:
        daily = rng.normal(drift, vol, len(dates))
        closes = start_price * np.cumprod(1 + daily)
        if symbol == "ALPHA":
            closes[1100:] *= 1.08  # synthetic event jump
        closes_by_symbol[symbol] = closes
        for day, close in zip(dates, closes, strict=True):
            price_rows.append({
                "symbol": symbol, "date": day.date().isoformat(), "open": close * 0.997,
                "high": close * 1.012, "low": close * 0.988, "close": close,
                "volume": 1_000_000, "currency": "USD", "provider": "demo",
                "adjustment": "synthetic_adjusted",
            })

    fundamental_rows: list[dict[str, object]] = []
    report_dates = pd.date_range(start=dates[0], end=dates[-1], freq="QE")
    for symbol, company, shares, base_revenue, base_income, base_book in (
        ("ALPHA", "Alpha Systems", 1_000_000_000, 28e9, 4.2e9, 20e9),
        ("BETA", "Beta Industrial", 800_000_000, 42e9, 2.4e9, 18e9),
    ):
        for idx, report_date in enumerate(report_dates):
            years = idx / 4
            revenue = base_revenue * (1.10 if symbol == "ALPHA" else 1.055) ** years
            income = base_income * (1.14 if symbol == "ALPHA" else 1.045) ** years
            book = base_book * (1.09 if symbol == "ALPHA" else 1.04) ** years
            price_index = min(np.searchsorted(dates.values, report_date.to_datetime64(), side="right") - 1, len(dates) - 1)
            price_index = max(price_index, 0)
            price = float(closes_by_symbol[symbol][price_index])
            market_cap = price * shares
            debt = 9e9 if symbol == "ALPHA" else 14e9
            cash = 13e9 if symbol == "ALPHA" else 4.8e9
            minority = 0.6e9 if symbol == "ALPHA" else 0.2e9
            ebitda = income * (1.35 if symbol == "ALPHA" else 1.65)
            ocf = income * 1.25
            capex = revenue * (0.065 if symbol == "ALPHA" else 0.05)
            fundamental_rows.append({
                "symbol": symbol, "company": company, "as_of": report_date.date().isoformat(),
                "currency": "USD", "fiscal_window": f"Synthetic TTM ending {report_date.date().isoformat()}",
                "price": price, "shares_outstanding": shares, "market_cap": market_cap,
                "enterprise_value": market_cap + debt + minority - cash, "revenue_ttm": revenue,
                "net_income_ttm": income, "book_value": book, "ebitda_ttm": ebitda,
                "gross_profit_ttm": revenue * (0.55 if symbol == "ALPHA" else 0.30),
                "operating_income_ttm": income * 1.15, "operating_cash_flow_ttm": ocf,
                "capex_ttm": capex, "free_cash_flow_ttm": ocf - capex, "total_debt": debt,
                "cash": cash, "minority_interest": minority, "eps_ttm": income / shares,
                "eps_ttm_diluted": income / shares, "eps_ttm_ex_items": income / shares * 0.96,
                "eps_last_fy": income / shares * 0.92, "book_value_per_share": book / shares,
                "forward_eps": income / shares * (1.13 if symbol == "ALPHA" else 1.06),
                "eps_growth_3y_cagr": 0.18 if symbol == "ALPHA" else 0.08,
                "eps_growth_5y_cagr": 0.15 if symbol == "ALPHA" else 0.07,
                "analyst_eps_growth_5y": 0.14 if symbol == "ALPHA" else 0.065,
                "provider": "demo",
            })

    etf = pd.DataFrame([{
        "symbol": "510300.SS", "name": "Demo CSI 300 ETF", "as_of": dates[-1].date().isoformat(),
        "timestamp": now_utc(), "currency": "CNY", "market_price": 4.126, "iopv": 4.101,
        "nav": 4.095, "provider_reported_premium_pct": None, "cross_border": False, "provider": "demo",
    }])
    events = [{"id": "demo-event", "date": dates[1100].date().isoformat(), "symbols": ["ALPHA"], "title": "Synthetic product event"}]
    write_frame(run_dir / "data" / "prices.csv", pd.DataFrame(price_rows))
    write_frame(run_dir / "data" / "fundamentals.csv", pd.DataFrame(fundamental_rows))
    write_frame(run_dir / "data" / "etf_snapshot.csv", etf)
    write_json(run_dir / "data" / "events.json", events)
    manifest = RunManifest(
        status="completed", symbols=["ALPHA", "BETA", "SPY", "510300.SS"],
        requested_datasets=["prices", "fundamentals", "etf"],
        artifacts={
            "prices_csv": "data/prices.csv", "fundamentals_csv": "data/fundamentals.csv",
            "etf_snapshot_csv": "data/etf_snapshot.csv", "events_json": "data/events.json",
        },
        sources=[
            SourceRecord(provider="demo", dataset="prices", status="success", record_count=len(price_rows)),
            SourceRecord(provider="demo", dataset="fundamentals", status="success", record_count=len(fundamental_rows)),
            SourceRecord(provider="demo", dataset="etf", status="success", record_count=1),
        ],
        notes=["Synthetic deterministic data for offline testing; not investment data."],
    )
    write_json(run_dir / "manifest.json", manifest)
    return manifest
