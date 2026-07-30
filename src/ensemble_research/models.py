from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .config import now_utc


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataError(StrictModel):
    module: str
    message: str
    item: str | None = None
    recoverable: bool = True
    missing_inputs: list[str] = Field(default_factory=list)
    exception_type: str | None = None


class SourceRecord(StrictModel):
    provider: str
    dataset: str
    symbol: str | None = None
    status: Literal["success", "partial", "failed", "unsupported"]
    retrieved_at: str = Field(default_factory=now_utc)
    record_count: int = 0
    notes: list[str] = Field(default_factory=list)
    errors: list[DataError] = Field(default_factory=list)


class RunManifest(StrictModel):
    schema_version: str = "0.3.0"
    tool_version: str = "0.3.0"
    created_at: str = Field(default_factory=now_utc)
    updated_at: str = Field(default_factory=now_utc)
    status: Literal["running", "completed", "completed_with_warnings", "failed"] = "running"
    symbols: list[str] = Field(default_factory=list)
    query: str | None = None
    requested_datasets: list[str] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    sources: list[SourceRecord] = Field(default_factory=list)
    errors: list[DataError] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class MetricRecord(StrictModel):
    symbol: str
    metric: str
    value: float | None = None
    unit: str = "x"
    method: str
    formula: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    as_of: str | None = None
    fiscal_window: str | None = None
    currency: str | None = None
    provider: str | None = None
    source_dataset: str
    adjustment_policy: str | None = None
    status: Literal["valid", "unavailable", "invalid"] = "valid"
    not_meaningful: bool = False
    caveats: list[str] = Field(default_factory=list)

    def display(self) -> str:
        if self.not_meaningful or self.value is None:
            return "n.m." + (f" ({'; '.join(self.caveats)})" if self.caveats else "")
        if self.unit == "%":
            return f"{self.value:.1f}%"
        if self.unit == "x":
            return f"{self.value:.1f}x"
        return f"{self.value:,.2f} {self.unit}"


class ValidationIssue(StrictModel):
    severity: Literal["error", "warning", "info"]
    code: str
    message: str
    artifact: str | None = None
    row: int | None = None


class ValidationReport(StrictModel):
    generated_at: str = Field(default_factory=now_utc)
    valid: bool = True
    issues: list[ValidationIssue] = Field(default_factory=list)
    checked_artifacts: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
