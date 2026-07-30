from __future__ import annotations

from pathlib import Path

from ..io import read_json
from ..presentation.renderers import render_artifact
from ..validation.artifact_validator import validate_file


def validate_analyst_artifact(path: str | Path, schema: str, *, strict: bool = False) -> dict:
    return validate_file(path, schema, strict=strict)


def render_analyst_artifact(input_path: str | Path, output_path: str | Path, *, kind: str | None = None) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_artifact(read_json(input_path), kind), encoding="utf-8")
    return output
