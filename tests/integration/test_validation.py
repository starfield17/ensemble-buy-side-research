from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ensemble_research.application.metric_service import calculate_metrics
from ensemble_research.demo import create_demo_run
from ensemble_research.validation import validate_run


def test_validator_recomputes_multiple_formulas(tmp_path: Path):
    create_demo_run(tmp_path); calculate_metrics(tmp_path)
    metrics = pd.read_csv(tmp_path / "metrics" / "metrics.csv")
    idx = metrics.index[(metrics.symbol == "ALPHA") & (metrics.metric == "pe_ttm")][0]
    metrics.loc[idx, "value"] = 999
    metrics.to_csv(tmp_path / "metrics" / "metrics.csv", index=False)
    report = validate_run(tmp_path)
    assert not report.valid
    assert "metric_formula_mismatch" in {issue.code for issue in report.issues}


def test_manifest_rejects_unknown_fields(tmp_path: Path):
    create_demo_run(tmp_path); calculate_metrics(tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["unexpected"] = True
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    report = validate_run(tmp_path)
    assert not report.valid and "invalid_manifest" in {issue.code for issue in report.issues}
