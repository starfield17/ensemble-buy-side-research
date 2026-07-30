from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from .application.artifact_service import render_analyst_artifact, validate_analyst_artifact
from .application.metric_service import calculate_metrics
from .application.pipeline import fetch_data, load_manifest, save_manifest
from .config import load_settings, parse_csv
from .demo import create_demo_run
from .domain.metrics import build_multiple_series, percentile_of_latest, run_event_study
from .io import first_existing, read_frame, read_json, write_frame, write_json
from .presentation import generate_chart, generate_table
from .presentation.style import configure_fonts
from .validation import available_schemas, validate_run

app = typer.Typer(no_args_is_help=True, help="Auditable objective data tooling for buy-side research; no scoring or automatic investment verdicts.")
console = Console()


def _ok(message: str) -> None:
    console.print(f"[green]OK[/green] {message}")


def _warn(message: str) -> None:
    console.print(f"[yellow]WARN[/yellow] {message}")


def _register(run: Path, key: str, path: Path) -> None:
    manifest = load_manifest(run)
    manifest.artifacts[key] = str(path.relative_to(run))
    save_manifest(run, manifest)


def _growth_map(value: str | None) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in parse_csv(value):
        if "=" not in item:
            raise typer.BadParameter("--growth must use SYMBOL=RATE, e.g. AAPL=0.18")
        symbol, rate = item.split("=", 1)
        result[symbol.strip().upper()] = float(rate)
    return result


@app.command()
def fetch(
    output: Annotated[Path, typer.Option("--output", "-o", help="Run directory.")],
    symbols: Annotated[str, typer.Option(help="Comma-separated symbols.")] = "",
    datasets: Annotated[str, typer.Option(help="prices,fundamentals,etf,etf_prices,filings,news")] = "prices,fundamentals",
    provider: Annotated[str, typer.Option(help="auto,yfinance,akshare,tushare")] = "auto",
    start: Annotated[str | None, typer.Option()] = None,
    end: Annotated[str | None, typer.Option()] = None,
    query: Annotated[str | None, typer.Option(help="Required when dataset includes news.")] = None,
    formats: Annotated[str, typer.Option(help="csv,parquet,json")] = "csv",
) -> None:
    manifest = fetch_data(output, parse_csv(symbols), parse_csv(datasets), provider=provider, start=start, end=end, query=query, formats=parse_csv(formats))
    _ok(f"fetch completed with status={manifest.status}: {output}")
    for note in manifest.notes:
        _warn(note)
    for error in manifest.errors:
        _warn(f"{error.module}{' [' + error.item + ']' if error.item else ''}: {error.message}")
    if manifest.status == "failed":
        raise typer.Exit(code=1)


@app.command()
def metrics(
    run: Annotated[Path, typer.Option(help="Run directory containing data/.")],
    format: Annotated[str, typer.Option(help="csv,parquet,json")] = "csv",
    growth: Annotated[str | None, typer.Option(help="Optional analyst-supplied PEG growth: SYMBOL=0.18,SYMBOL2=12.5")] = None,
    cross_market: Annotated[bool, typer.Option(help="Attach cross-market comparability caveats.")] = False,
) -> None:
    frame, warnings = calculate_metrics(run, format, custom_growth_rates=_growth_map(growth), cross_market=cross_market)
    manifest = load_manifest(run)
    manifest.artifacts[f"metrics_{format}"] = f"metrics/metrics.{format}"
    manifest.artifacts["metric_definitions"] = "metrics/metric_definitions.json"
    manifest.notes.extend(warnings)
    save_manifest(run, manifest)
    _ok(f"calculated {len(frame)} metric rows")
    for warning in warnings:
        _warn(warning)


@app.command("table")
def table_command(
    run: Annotated[Path, typer.Option(help="Run directory.")],
    preset: Annotated[str, typer.Option(help="valuation-comparison,performance-summary,etf-premium,fundamental-snapshot,peg-comparison")] = "valuation-comparison",
    formats: Annotated[str, typer.Option(help="csv,markdown,json")] = "csv,markdown",
) -> None:
    outputs, warnings = generate_table(run, preset, parse_csv(formats))
    manifest = load_manifest(run)
    for path in outputs:
        manifest.artifacts[f"table_{preset}_{path.suffix.lstrip('.')}"] = str(path.relative_to(run))
    manifest.notes.extend(warnings); save_manifest(run, manifest)
    for path in outputs:
        _ok(f"wrote {path}")
    for warning in warnings:
        _warn(warning)


@app.command("chart")
def chart_command(
    run: Annotated[Path, typer.Option(help="Run directory.")],
    preset: Annotated[str, typer.Option(help="price-history,normalized-performance,metric-comparison,etf-premium,valuation-band,event-returns")] = "price-history",
    metric: Annotated[str | None, typer.Option(help="Required for metric-comparison.")] = None,
) -> None:
    path = generate_chart(run, preset, metric)
    manifest = load_manifest(run)
    key = f"chart_{preset}{'_' + metric if metric else ''}"
    manifest.artifacts[key] = str(path.relative_to(run))
    manifest.artifacts[f"{key}_data"] = str(path.with_suffix(".csv").relative_to(run))
    save_manifest(run, manifest)
    _ok(f"wrote {path} and {path.with_suffix('.csv')}")


@app.command()
def percentile(
    run: Annotated[Path, typer.Option(help="Run directory with prices and fundamentals.")],
    symbol: Annotated[str, typer.Option(help="Symbol to analyze.")],
    metric: Annotated[str, typer.Option(help="pe_ttm,pb,ps_ttm")] = "pe_ttm",
    lookback_years: Annotated[float, typer.Option(min=0.25)] = 5.0,
) -> None:
    price_path = first_existing(run, "prices"); fund_path = first_existing(run, "fundamentals")
    if price_path is None or fund_path is None:
        raise typer.BadParameter("prices and fundamentals datasets are both required")
    series = build_multiple_series(read_frame(price_path), read_frame(fund_path), symbol=symbol.upper(), metric=metric)
    result = percentile_of_latest(series, metric_name=metric, lookback_years=lookback_years)
    series_path = Path(run) / "analysis" / "percentile-series.csv"
    result_path = Path(run) / "analysis" / "percentile.json"
    write_frame(series_path, series); write_json(result_path, result)
    manifest = load_manifest(run)
    manifest.artifacts["percentile_series"] = str(series_path.relative_to(run))
    manifest.artifacts["percentile_result"] = str(result_path.relative_to(run))
    save_manifest(run, manifest)
    _ok(f"wrote {result_path}; percentile={result.get('percentile')}")
    if result.get("coverage_warning"):
        _warn(result["coverage_warning"])
    if result.get("not_meaningful"):
        _warn(result.get("caveat", "Percentile is not meaningful."))


@app.command("event-study")
def event_study_command(
    run: Annotated[Path, typer.Option(help="Run directory containing prices.")],
    events: Annotated[Path, typer.Option(help="JSON list of events.")],
    benchmark: Annotated[str | None, typer.Option(help="Benchmark symbol contained in prices.")] = None,
    model: Annotated[str, typer.Option(help="raw,market-adjusted,market-model")] = "market-adjusted",
) -> None:
    price_path = first_existing(run, "prices")
    if price_path is None:
        raise typer.BadParameter("prices dataset is required")
    payload = read_json(events)
    if not isinstance(payload, list):
        raise typer.BadParameter("events JSON must be a list")
    result = run_event_study(payload, read_frame(price_path), benchmark=benchmark, model=model)
    out = Path(run) / "analysis" / "event-study.csv"
    write_frame(out, result); _register(Path(run), "event_study", out)
    _ok(f"wrote {out} ({len(result)} rows)")


@app.command("validate-run")
def validate_run_command(run: Annotated[Path, typer.Option(help="Run directory.")]) -> None:
    report = validate_run(run)
    manifest = load_manifest(run); manifest.artifacts["validation"] = "validation.json"; save_manifest(run, manifest)
    if report.valid:
        _ok(f"run is valid ({report.summary})")
    else:
        console.print(f"[red]INVALID[/red] {report.summary}"); raise typer.Exit(code=1)


@app.command("validate")
def validate_compat(run: Annotated[Path, typer.Option(help="Run directory.")]) -> None:
    validate_run_command(run)


@app.command("validate-artifact")
def validate_artifact_command(
    file: Annotated[Path, typer.Option(help="Analyst-authored JSON artifact.")],
    schema: Annotated[str, typer.Option(help=f"Schema name; typical values: {','.join(available_schemas())}")],
    strict: Annotated[bool, typer.Option(help="Treat placeholders as errors.")] = False,
) -> None:
    result = validate_analyst_artifact(file, schema, strict=strict)
    console.print_json(data=result)
    if not result["valid"]:
        raise typer.Exit(code=1)


@app.command("render-artifact")
def render_artifact_command(
    input: Annotated[Path, typer.Option(help="Analyst-authored JSON artifact.")],
    output: Annotated[Path, typer.Option(help="Markdown destination.")],
    kind: Annotated[str | None, typer.Option(help="Optional explicit renderer kind.")] = None,
) -> None:
    path = render_analyst_artifact(input, output, kind=kind); _ok(f"wrote {path}")


@app.command()
def doctor() -> None:
    settings = load_settings(); font = configure_fonts()
    packages = {name: importlib.util.find_spec(name) is not None for name in ("pandas", "numpy", "matplotlib", "yfinance", "akshare", "tushare", "jsonschema", "pyarrow")}
    console.print("[bold]Packages[/bold]")
    for name, installed in packages.items():
        console.print(f"  {'OK' if installed else 'MISSING'} {name}")
    console.print("[bold]Credentials[/bold]")
    console.print(f"  {'OK' if settings.sec_user_agent else 'MISSING'} SEC_USER_AGENT")
    console.print(f"  {'OK' if settings.tushare_token else 'MISSING'} TUSHARE_TOKEN")
    console.print(f"[bold]CJK font[/bold]\n  {font or 'No preferred CJK font detected; charts still use the default font.'}")


def _safe_table(run: Path, preset: str) -> None:
    try:
        outputs, warnings = generate_table(run, preset, ["csv", "markdown"])
        manifest = load_manifest(run)
        for path in outputs:
            manifest.artifacts[f"table_{preset}_{path.suffix.lstrip('.')}"] = str(path.relative_to(run))
        manifest.notes.extend(warnings); save_manifest(run, manifest)
    except Exception as exc:
        _warn(f"table {preset} skipped: {exc}")


def _safe_chart(run: Path, preset: str, metric: str | None = None) -> None:
    try:
        path = generate_chart(run, preset, metric)
        manifest = load_manifest(run); key = f"chart_{preset}{'_' + metric if metric else ''}"
        manifest.artifacts[key] = str(path.relative_to(run)); manifest.artifacts[f"{key}_data"] = str(path.with_suffix('.csv').relative_to(run)); save_manifest(run, manifest)
    except Exception as exc:
        _warn(f"chart {preset} skipped: {exc}")


@app.command()
def demo(output: Annotated[Path, typer.Option("--output", "-o", help="Demo run directory.")] = Path("runs/demo")) -> None:
    create_demo_run(output)
    calculate_metrics(output)
    manifest = load_manifest(output); manifest.artifacts.update({"metrics_csv": "metrics/metrics.csv", "metric_definitions": "metrics/metric_definitions.json"}); save_manifest(output, manifest)
    for preset in ("valuation-comparison", "performance-summary", "etf-premium", "fundamental-snapshot", "peg-comparison"):
        _safe_table(output, preset)
    for preset in ("price-history", "normalized-performance", "etf-premium"):
        _safe_chart(output, preset)
    _safe_chart(output, "metric-comparison", "pe_ttm")
    price_path = first_existing(output, "prices"); fund_path = first_existing(output, "fundamentals")
    if price_path and fund_path:
        series = build_multiple_series(read_frame(price_path), read_frame(fund_path), symbol="ALPHA", metric="pe_ttm")
        result = percentile_of_latest(series, metric_name="pe_ttm", lookback_years=5)
        write_frame(output / "analysis" / "percentile-series.csv", series); write_json(output / "analysis" / "percentile.json", result)
        manifest = load_manifest(output); manifest.artifacts.update({"percentile_series": "analysis/percentile-series.csv", "percentile_result": "analysis/percentile.json"}); save_manifest(output, manifest)
        _safe_chart(output, "valuation-band")
        events = read_json(output / "data" / "events.json")
        study = run_event_study(events, read_frame(price_path), benchmark="SPY", model="market_adjusted")
        write_frame(output / "analysis" / "event-study.csv", study)
        manifest = load_manifest(output); manifest.artifacts["event_study"] = "analysis/event-study.csv"; save_manifest(output, manifest)
        _safe_chart(output, "event-returns")
    report = validate_run(output)
    manifest = load_manifest(output); manifest.artifacts["validation"] = "validation.json"; save_manifest(output, manifest)
    _ok(f"demo generated at {output}; valid={report.valid}, summary={report.summary}")
    if not report.valid:
        raise typer.Exit(code=1)


@app.command()
def run(
    output: Annotated[Path, typer.Option("--output", "-o")],
    symbols: Annotated[str, typer.Option()] = "",
    datasets: Annotated[str, typer.Option()] = "prices,fundamentals,etf",
    provider: Annotated[str, typer.Option()] = "auto",
    start: Annotated[str | None, typer.Option()] = None,
    end: Annotated[str | None, typer.Option()] = None,
    query: Annotated[str | None, typer.Option()] = None,
    growth: Annotated[str | None, typer.Option(help="Optional custom PEG assumptions.")] = None,
    cross_market: Annotated[bool, typer.Option()] = False,
) -> None:
    manifest = fetch_data(output, parse_csv(symbols), parse_csv(datasets), provider=provider, start=start, end=end, query=query, formats=["csv"])
    if manifest.status == "failed":
        raise typer.Exit(code=1)
    calculate_metrics(output, custom_growth_rates=_growth_map(growth), cross_market=cross_market)
    manifest = load_manifest(output); manifest.artifacts.update({"metrics_csv": "metrics/metrics.csv", "metric_definitions": "metrics/metric_definitions.json"}); save_manifest(output, manifest)
    for preset in ("valuation-comparison", "performance-summary", "etf-premium", "fundamental-snapshot"):
        _safe_table(output, preset)
    for preset in ("price-history", "normalized-performance", "etf-premium"):
        _safe_chart(output, preset)
    report = validate_run(output)
    manifest = load_manifest(output); manifest.artifacts["validation"] = "validation.json"; save_manifest(output, manifest)
    _ok(f"run completed: valid={report.valid}, summary={report.summary}")
    if not report.valid:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
