from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from ..io import first_existing, read_frame, read_json, write_json
from ..models import RunManifest, ValidationIssue, ValidationReport

REQUIRED_COLUMNS = {
    "prices": {"symbol", "date", "close", "provider"},
    "fundamentals": {"symbol", "as_of", "provider"},
    "etf_snapshot": {"symbol", "as_of", "market_price", "provider"},
}


def _issue(issues, severity, code, message, artifact=None, row=None):
    issues.append(ValidationIssue(severity=severity, code=code, message=message, artifact=artifact, row=row))


def _validate_frame(name: str, path: Path, issues: list[ValidationIssue]) -> None:
    try:
        frame = read_frame(path)
    except Exception as exc:
        _issue(issues, "error", "unreadable_table", str(exc), str(path)); return
    missing = sorted(REQUIRED_COLUMNS.get(name, set()) - set(frame.columns))
    if missing:
        _issue(issues, "error", "missing_columns", f"Missing required columns: {', '.join(missing)}", str(path))
    if "symbol" in frame and frame["symbol"].isna().any():
        _issue(issues, "error", "missing_symbol", "One or more rows have no symbol.", str(path))
    if name == "prices" and {"symbol", "date"}.issubset(frame.columns):
        duplicates = int(frame.duplicated(["symbol", "date", "provider"] if "provider" in frame else ["symbol", "date"]).sum())
        if duplicates:
            _issue(issues, "warning", "duplicate_prices", f"Found {duplicates} duplicate price rows.", str(path))
        invalid = int(pd.to_datetime(frame["date"], errors="coerce").isna().sum())
        if invalid:
            _issue(issues, "error", "invalid_dates", f"Found {invalid} invalid price dates.", str(path))
        nonpositive = int((pd.to_numeric(frame["close"], errors="coerce") <= 0).sum())
        if nonpositive:
            _issue(issues, "warning", "nonpositive_close", f"Found {nonpositive} non-positive closes.", str(path))


def _inputs(value) -> dict:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value:
        return {}
    return json.loads(value)


def _f(inputs: dict, name: str) -> float:
    value = inputs[name]
    if value is None:
        raise ValueError(name)
    return float(value)


def _recompute(metric: str, inputs: dict) -> float | None:
    ratio_map = {
        "pe_ttm": [("market_cap", "net_income_ttm", 1.0), ("price", "eps_ttm_diluted", 1.0)],
        "pe_ttm_ex_items": [("price", "eps_ttm_ex_items", 1.0)],
        "pe_static": [("price", "eps_last_fy", 1.0)],
        "pe_forward": [("price", "forward_eps", 1.0)],
        "pb": [("market_cap", "book_value", 1.0), ("price", "book_value_per_share", 1.0)],
        "ps_ttm": [("market_cap", "revenue_ttm", 1.0)],
        "ev_ebitda": [("enterprise_value", "ebitda_ttm", 1.0)],
        "fcf_yield": [("free_cash_flow_ttm", "market_cap", 100.0)],
        "roe": [("net_income_ttm", "book_value", 100.0)],
        "debt_to_equity": [("total_debt", "book_value", 1.0)],
        "gross_margin": [("gross_profit_ttm", "revenue_ttm", 100.0)],
        "operating_margin": [("operating_income_ttm", "revenue_ttm", 100.0)],
        "peg_historical_3y": [("pe_ttm", "eps_growth_3y_cagr_percentage_points", 1.0)],
        "peg_historical_5y": [("pe_ttm", "eps_growth_5y_cagr_percentage_points", 1.0)],
        "peg_forward_consensus": [("pe_ttm", "analyst_eps_growth_5y_percentage_points", 1.0)],
        "peg_custom": [("pe_ttm", "custom_growth_percentage_points", 1.0)],
        "premium_to_iopv": [("market_price", "iopv", 100.0)],
        "premium_to_nav": [("market_price", "nav", 100.0)],
    }
    if metric in {"premium_to_iopv", "premium_to_nav"}:
        numerator, denominator, _ = ratio_map[metric][0]
        return (_f(inputs, numerator) / _f(inputs, denominator) - 1.0) * 100.0
    for numerator, denominator, multiplier in ratio_map.get(metric, []):
        if numerator in inputs and denominator in inputs and inputs.get(numerator) is not None and inputs.get(denominator) is not None:
            return _f(inputs, numerator) / _f(inputs, denominator) * multiplier
    if metric == "period_return":
        return (_f(inputs, "last_close") / _f(inputs, "first_close") - 1.0) * 100.0
    return None


def _validate_metrics(path: Path, issues: list[ValidationIssue]) -> None:
    try:
        frame = read_frame(path)
    except Exception as exc:
        _issue(issues, "error", "unreadable_metrics", str(exc), str(path)); return
    required = {"symbol", "metric", "value", "method", "formula", "inputs", "status", "source_dataset", "not_meaningful"}
    missing = sorted(required - set(frame.columns))
    if missing:
        _issue(issues, "error", "missing_metric_columns", f"Missing required columns: {', '.join(missing)}", str(path)); return
    invalid_status = frame[~frame["status"].isin(["valid", "unavailable", "invalid"])]
    if not invalid_status.empty:
        _issue(issues, "error", "invalid_metric_status", f"Found {len(invalid_status)} rows with invalid status.", str(path))
    if not frame[(frame["status"] == "valid") & frame["value"].isna()].empty:
        _issue(issues, "error", "valid_metric_missing_value", "Valid metric rows must contain a value.", str(path))
    for index, row in frame.iterrows():
        if row.get("status") != "valid" or pd.isna(row.get("value")):
            continue
        try:
            expected = _recompute(str(row["metric"]), _inputs(row.get("inputs")))
            if expected is not None and (not math.isfinite(expected) or abs(expected - float(row["value"])) > 1e-7 * max(1.0, abs(expected))):
                _issue(issues, "error", "metric_formula_mismatch", f"Stored {row['metric']} does not match its inputs.", str(path), int(index))
        except Exception as exc:
            _issue(issues, "warning", "metric_inputs_unreadable", f"Could not independently verify {row.get('metric')}: {exc}", str(path), int(index))


def validate_run(run_dir: str | Path, write: bool = True) -> ValidationReport:
    run_dir = Path(run_dir); issues: list[ValidationIssue] = []; checked: list[str] = []
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        _issue(issues, "error", "missing_manifest", "manifest.json is missing.", str(manifest_path))
    else:
        checked.append(str(manifest_path))
        try:
            manifest = RunManifest.model_validate(read_json(manifest_path))
            if manifest.status == "failed":
                _issue(issues, "error", "failed_run", "Manifest reports that the data run failed.", str(manifest_path))
            for name, relative in manifest.artifacts.items():
                if not (run_dir / relative).exists():
                    _issue(issues, "error", "missing_artifact", f"Manifest artifact does not exist: {name} -> {relative}", str(manifest_path))
        except (ValidationError, ValueError) as exc:
            _issue(issues, "error", "invalid_manifest", str(exc), str(manifest_path))
    for name in REQUIRED_COLUMNS:
        path = first_existing(run_dir, name)
        if path:
            checked.append(str(path)); _validate_frame(name, path, issues)
    metric_path = first_existing(run_dir, "metrics", folder="metrics")
    if metric_path:
        checked.append(str(metric_path)); _validate_metrics(metric_path, issues)
    else:
        _issue(issues, "warning", "missing_metrics", "No metrics artifact found.")
    errors = sum(issue.severity == "error" for issue in issues); warnings = sum(issue.severity == "warning" for issue in issues)
    report = ValidationReport(valid=errors == 0, issues=issues, checked_artifacts=checked, summary={"errors": errors, "warnings": warnings, "checked": len(checked)})
    if write:
        write_json(run_dir / "validation.json", report)
    return report
