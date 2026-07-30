from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..io import first_existing, read_frame, write_frame

PRESETS = {
    "valuation-comparison": ["pe_ttm", "pe_forward", "pb", "ps_ttm", "ev_ebitda", "fcf_yield"],
    "performance-summary": ["period_return", "annualized_volatility", "max_drawdown"],
    "etf-premium": ["premium_to_iopv", "premium_to_nav"],
    "fundamental-snapshot": ["roe", "debt_to_equity", "gross_margin", "operating_margin"],
    "peg-comparison": ["peg_historical_3y", "peg_historical_5y", "peg_forward_consensus", "peg_custom"],
}


def _metrics_path(run_dir: Path) -> Path | None:
    return first_existing(run_dir, "metrics", folder="metrics")


def _decode_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, list) else [str(decoded)]
        except Exception:
            return [value]
    return []


def generate_table(run_dir: str | Path, preset: str, formats: list[str]) -> tuple[list[Path], list[str]]:
    run_dir = Path(run_dir)
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset {preset!r}; choose from {sorted(PRESETS)}")
    path = _metrics_path(run_dir)
    if path is None:
        raise FileNotFoundError("No metrics dataset found; run metrics first.")
    frame = read_frame(path)
    selected = frame[frame["metric"].isin(PRESETS[preset])].copy()
    warnings: list[str] = []
    if selected.empty:
        warnings.append(f"No metric rows matched preset {preset}.")
        table = pd.DataFrame(columns=["symbol", *PRESETS[preset]])
    else:
        table = selected.pivot_table(index="symbol", columns="metric", values="value", aggfunc="last").reset_index()
        status = selected.pivot_table(index="symbol", columns="metric", values="status", aggfunc="last").reset_index()
        status = status.rename(columns={col: f"{col}__status" for col in status.columns if col != "symbol"})
        table = table.merge(status, on="symbol", how="left")
        methods = selected.groupby("metric")["method"].agg(lambda values: " | ".join(sorted(set(str(v) for v in values if pd.notna(v))))).to_dict()
        caveat_rows = []
        for _, row in selected.iterrows():
            caveats = _decode_list(row.get("caveats"))
            if caveats:
                caveat_rows.append({"symbol": row["symbol"], "metric": row["metric"], "caveats": "; ".join(caveats)})
    outputs: list[Path] = []
    for fmt in formats:
        fmt = fmt.lower()
        out = run_dir / "tables" / f"{preset}.{fmt if fmt != 'markdown' else 'md'}"
        out.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "csv":
            write_frame(out, table)
        elif fmt == "json":
            write_frame(out, table)
        elif fmt in {"markdown", "md"}:
            lines = [f"# {preset.replace('-', ' ').title()}", "", table.to_markdown(index=False), "", "## Method tags", ""]
            if selected.empty:
                lines.append("- No matching metrics.")
            else:
                for metric in PRESETS[preset]:
                    if metric in methods:
                        lines.append(f"- `{metric}`: {methods[metric]}")
                lines += ["", "> Descriptive metrics only. No ranking, score, or investment verdict is implied."]
                if caveat_rows:
                    lines += ["", "## Caveats", ""] + [f"- {r['symbol']} / `{r['metric']}`: {r['caveats']}" for r in caveat_rows]
            out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            warnings.append(f"Unsupported table format ignored: {fmt}")
            continue
        outputs.append(out)
    return outputs, warnings
