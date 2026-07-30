from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: str | Path, data: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(data, "model_dump"):
        data = data.model_dump(exclude_none=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_frame(path: str | Path, frame: pd.DataFrame) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False)
    elif suffix == ".parquet":
        frame.to_parquet(path, index=False)
    elif suffix == ".json":
        frame.to_json(path, orient="records", force_ascii=False, indent=2, date_format="iso")
    else:
        raise ValueError(f"Unsupported table format: {suffix}")
    return path


def read_frame(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported table format: {suffix}")


def first_existing(run_dir: str | Path, stem: str, *, folder: str = "data") -> Path | None:
    run_dir = Path(run_dir)
    for suffix in (".parquet", ".csv", ".json"):
        candidate = run_dir / folder / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    return None


def save_table_formats(run_dir: str | Path, stem: str, frame: pd.DataFrame, formats: list[str], *, folder: str = "data") -> tuple[dict[str, str], list[str]]:
    run_dir = Path(run_dir)
    artifacts: dict[str, str] = {}
    warnings: list[str] = []
    for fmt in formats:
        fmt = fmt.lower().strip()
        if fmt not in {"csv", "parquet", "json"}:
            warnings.append(f"Unsupported output format ignored: {fmt}")
            continue
        path = run_dir / folder / f"{stem}.{fmt}"
        try:
            write_frame(path, frame)
            artifacts[f"{stem}_{fmt}"] = str(path.relative_to(run_dir))
        except Exception as exc:
            warnings.append(f"Could not write {path.name}: {exc}")
    return artifacts, warnings
