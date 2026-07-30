from __future__ import annotations

import pandas as pd

from ensemble_research.infrastructure.connectors.tushare import _sum_debt, _ttm
from ensemble_research.validation.artifact_validator import find_placeholders, validate_artifact


def test_tushare_ttm_reconstructs_four_discrete_quarters():
    frame = pd.DataFrame([
        {"end_date": "20250331", "ann_date": "20250430", "report_type": "1", "x": 10},
        {"end_date": "20250630", "ann_date": "20250830", "report_type": "1", "x": 25},
        {"end_date": "20250930", "ann_date": "20251030", "report_type": "1", "x": 45},
        {"end_date": "20251231", "ann_date": "20260330", "report_type": "1", "x": 70},
    ])
    value, window = _ttm(frame, "x")
    assert value == 70.0 and window.startswith("TTM")


def test_tushare_debt_never_uses_total_liabilities():
    debt, notes = _sum_debt(pd.Series({"total_liab": 999.0}))
    assert debt is None and "deliberately not substituted" in notes[0]
    debt, _ = _sum_debt(pd.Series({"st_borr": 10.0, "lt_borr": 20.0, "total_liab": 999.0}))
    assert debt == 30.0


def test_placeholders_are_detected_at_depth():
    found = find_placeholders({"a": {"b": [{"c": "TODO: fill in"}]}})
    assert len(found) == 1 and "$.a.b[0].c" in found[0]


def test_thesis_without_falsification_fails_schema():
    artifact = {
        "direction": "AI inference", "statement": "x" * 50, "consensus": "y" * 40,
        "variant_view": "z" * 50, "layer": "memory", "time_horizon": "12m",
        "variables": ["gross margin"], "falsification": [], "judgment": "D. Potential Investment Thesis",
    }
    assert validate_artifact(artifact, "thesis")["valid"] is False
