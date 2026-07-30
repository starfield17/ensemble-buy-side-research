from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..io import read_json

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.IGNORECASE), re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"<[a-z_ ]{3,40}>", re.IGNORECASE), re.compile(r"^\s*\[[^\]]{3,160}\]\s*$"),
    re.compile(r"\bfill in\b", re.IGNORECASE), re.compile(r"\blorem ipsum\b", re.IGNORECASE),
]
_JSON_TYPES: dict[str, Any] = {
    "object": dict, "array": list, "string": str, "number": (int, float),
    "integer": int, "boolean": bool, "null": type(None),
}


def _schema_dirs() -> list[Path]:
    here = Path(__file__).resolve()
    return [here.parents[3] / "schemas", here.parents[1] / "resources" / "schemas"]


def _schema_dir() -> Path:
    for path in _schema_dirs():
        if path.exists():
            return path
    return _schema_dirs()[0]


def available_schemas() -> list[str]:
    return sorted(path.stem.replace(".schema", "") for path in _schema_dir().glob("*.schema.json"))


def load_schema(name: str) -> dict[str, Any]:
    path = _schema_dir() / f"{name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"no schema named {name!r}; available: {', '.join(available_schemas()) or 'none'}")
    return read_json(path)


def _fallback_validate(data: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        types = expected if isinstance(expected, list) else [expected]
        if not any(isinstance(data, _JSON_TYPES[t]) for t in types if t in _JSON_TYPES):
            return [f"{path}: expected type {expected}, got {type(data).__name__}"]
    if isinstance(data, dict):
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"{path}: missing required field {field!r}")
        for key, subschema in (schema.get("properties") or {}).items():
            if key in data:
                errors.extend(_fallback_validate(data[key], subschema, f"{path}.{key}"))
    elif isinstance(data, list):
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: expected at least {schema['minItems']} items, got {len(data)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(data):
                errors.extend(_fallback_validate(item, item_schema, f"{path}[{index}]"))
    elif isinstance(data, str) and "minLength" in schema and len(data) < schema["minLength"]:
        errors.append(f"{path}: string is {len(data)} chars, minimum {schema['minLength']}")
    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: expected {schema['const']!r}, got {data!r}")
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data!r} is not one of {schema['enum']}")
    return errors


def find_placeholders(data: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(data, str):
        for pattern in PLACEHOLDER_PATTERNS:
            match = pattern.search(data)
            if match:
                found.append(f"{path}: unfilled placeholder {match.group(0)!r}")
                break
    elif isinstance(data, dict):
        for key, value in data.items():
            found.extend(find_placeholders(value, f"{path}.{key}"))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            found.extend(find_placeholders(item, f"{path}[{index}]"))
    return found


def validate_artifact(data: Any, schema_name: str, *, strict: bool = False) -> dict[str, Any]:
    schema = load_schema(schema_name)
    try:
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(schema)
        errors = [f"{'.'.join(str(p) for p in error.path) or '$'}: {error.message}" for error in sorted(validator.iter_errors(data), key=str)]
        engine = "jsonschema"
    except ImportError:
        errors = _fallback_validate(data, schema)
        engine = "builtin-fallback (install jsonschema for full validation)"
    placeholders = find_placeholders(data)
    if strict:
        errors.extend(placeholders); placeholders = []
    return {"schema": schema_name, "validator": engine, "valid": not errors, "errors": errors, "warnings": placeholders}


def validate_file(path: str | Path, schema_name: str, *, strict: bool = False) -> dict[str, Any]:
    result = validate_artifact(read_json(path), schema_name, strict=strict)
    result["file"] = str(path)
    return result
