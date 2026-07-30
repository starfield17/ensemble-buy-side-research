from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_demo_cli_runs_end_to_end(tmp_path: Path) -> None:
    output = tmp_path / "demo"
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy(); env["PYTHONPATH"] = str(root / "src")
    subprocess.run([sys.executable, "-m", "ensemble_research", "demo", "--output", str(output)], check=True, env=env, cwd=root)
    for path in (
        output / "manifest.json", output / "metrics" / "metrics.csv", output / "charts" / "price-history.png",
        output / "charts" / "price-history.csv", output / "analysis" / "percentile.json",
        output / "analysis" / "event-study.csv", output / "validation.json",
    ):
        assert path.exists() and path.stat().st_size > 0
    metrics = pd.read_csv(output / "metrics" / "metrics.csv")
    assert {"method", "provider", "currency", "fiscal_window", "inputs", "caveats", "not_meaningful"}.issubset(metrics.columns)
