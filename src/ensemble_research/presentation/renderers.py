from __future__ import annotations

from typing import Any, Iterable, Mapping

MISSING = "Source needed"


def _cell(value: Any) -> str:
    if value is None or value == "" or value == []:
        return MISSING
    if isinstance(value, dict):
        return ", ".join(f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value) or MISSING
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown_table(rows: Iterable[Mapping[str, Any]], columns: list[tuple[str, str]]) -> str:
    header = "| " + " | ".join(head for head, _ in columns) + " |"
    divider = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(_cell(row.get(key)) for _, key in columns) + " |" for row in rows]
    return "\n".join([header, divider, *(body or ["| " + " | ".join(MISSING for _ in columns) + " |"])])


def render_value_chain(artifact: Mapping[str, Any]) -> str:
    columns = [
        ("Layer", "name"), ("Problem solved", "problem_solved"), ("Players", "players"),
        ("Bottleneck", "bottleneck"), ("Profit pool", "profit_pool_quality"),
        ("Competition", "competition"), ("Commoditization", "commoditization_risk"),
        ("Judgment", "judgment"),
    ]
    return f"## Value Chain Map — {artifact.get('direction', MISSING)}\n\n{markdown_table(artifact.get('layers', []), columns)}\n"


def render_watchlist(artifact: Mapping[str, Any]) -> str:
    columns = [
        ("Variable", "variable"), ("Why it matters", "why_it_matters"), ("Source", "source"),
        ("Frequency", "frequency"), ("Bullish threshold", "bullish_threshold"),
        ("Bearish threshold", "bearish_threshold"), ("Current", "current_reading"),
        ("Next check", "next_check"),
    ]
    return f"## Data Watchlist\n\n{markdown_table(artifact.get('items', []), columns)}\n"


def render_percentile(artifact: Mapping[str, Any]) -> str:
    if artifact.get("percentile") is None:
        return f"## Valuation percentile\n\n{MISSING} — {artifact.get('caveat', 'not computable')}\n"
    return (
        "## Valuation percentile\n\n"
        f"**{artifact.get('symbol', '')} {artifact['metric']}** is **{artifact['latest']:.1f}x**, at the "
        f"**{artifact['percentile']}th percentile** over {artifact['lookback_years_actual']} years "
        f"({artifact['window_start']} to {artifact['window_end']}, {artifact['observations']} observations).\n\n"
        f"> {artifact.get('caveat', '')}\n"
    )


def render_artifact(artifact: Mapping[str, Any], kind: str | None = None) -> str:
    kind = kind or artifact.get("kind")
    if kind is None:
        if "layers" in artifact:
            kind = "value_chain"
        elif "items" in artifact:
            kind = "watchlist"
        elif "percentile" in artifact:
            kind = "percentile"
    renderers = {"value_chain": render_value_chain, "watchlist": render_watchlist, "percentile": render_percentile}
    if kind in renderers:
        return renderers[str(kind)](artifact)
    lines = [f"# {str(kind or 'Artifact').replace('_', ' ').title()}", ""]
    for key, value in artifact.items():
        if key in {"kind", "schema_version"}:
            continue
        lines += [f"## {key.replace('_', ' ').title()}", "", _cell(value), ""]
    return "\n".join(lines).rstrip() + "\n"
