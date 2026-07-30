from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..io import first_existing, read_frame
from .style import configure_fonts


def _metrics_path(run_dir: Path) -> Path | None:
    return first_existing(run_dir, "metrics", folder="metrics")


def _save(fig, path: Path, data: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    data.to_csv(path.with_suffix(".csv"), index=False)
    return path


def _price_history(run_dir: Path, normalized: bool = False) -> Path:
    path = first_existing(run_dir, "prices")
    if path is None:
        raise FileNotFoundError("No prices dataset found.")
    frame = read_frame(path)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"])
    plotted: list[pd.DataFrame] = []
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for symbol, group in frame.groupby("symbol"):
        group = group.sort_values("date").copy()
        group["plotted_value"] = group["close"]
        if normalized and not group.empty and group["close"].iloc[0] != 0:
            group["plotted_value"] = group["close"] / group["close"].iloc[0] * 100.0
        ax.plot(group["date"], group["plotted_value"], label=str(symbol))
        plotted.append(group[["symbol", "date", "close", "plotted_value", "provider", "adjustment"]] if {"provider", "adjustment"}.issubset(group.columns) else group[["symbol", "date", "close", "plotted_value"]])
    ax.set_title("Normalized Performance (Start = 100)" if normalized else "Price History")
    ax.set_xlabel("Date"); ax.set_ylabel("Index" if normalized else "Price")
    ax.grid(True, alpha=0.25)
    if frame["symbol"].nunique() > 1:
        ax.legend()
    name = "normalized-performance.png" if normalized else "price-history.png"
    return _save(fig, run_dir / "charts" / name, pd.concat(plotted, ignore_index=True) if plotted else pd.DataFrame())


def _metric_comparison(run_dir: Path, metric: str) -> Path:
    path = _metrics_path(run_dir)
    if path is None:
        raise FileNotFoundError("No metrics dataset found.")
    frame = read_frame(path)
    frame = frame[(frame["metric"] == metric) & frame["value"].notna() & (frame["status"] == "valid")].copy()
    if frame.empty:
        raise ValueError(f"No valid values found for metric {metric}.")
    # Keep input/symbol order. Sorting would visually imply a desirability ranking.
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["value"])
    fig, ax = plt.subplots(figsize=(9, max(4.5, len(frame) * 0.45)))
    ax.barh(frame["symbol"].astype(str), frame["value"])
    unit = str(frame["unit"].iloc[0]) if "unit" in frame.columns else ""
    ax.set_title(metric.replace("_", " ").upper()); ax.set_xlabel(unit); ax.grid(True, axis="x", alpha=0.25)
    sidecar_cols = [col for col in ("symbol", "metric", "value", "unit", "method", "as_of", "provider", "currency", "fiscal_window") if col in frame.columns]
    return _save(fig, run_dir / "charts" / f"metric-{metric}.png", frame[sidecar_cols])


def _etf_premium(run_dir: Path) -> Path:
    path = _metrics_path(run_dir)
    if path is None:
        raise FileNotFoundError("No metrics dataset found.")
    frame = read_frame(path)
    frame = frame[frame["metric"].isin(["premium_to_iopv", "premium_to_nav"]) & frame["value"].notna()].copy()
    if frame.empty:
        raise ValueError("No valid ETF premium metrics found.")
    frame["label"] = frame["symbol"].astype(str) + " / " + frame["metric"].astype(str)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    fig, ax = plt.subplots(figsize=(9, max(4.5, len(frame) * 0.45)))
    ax.barh(frame["label"], frame["value"]); ax.axvline(0, linewidth=0.8)
    ax.set_title("ETF Premium / Discount"); ax.set_xlabel("Percentage points"); ax.grid(True, axis="x", alpha=0.25)
    sidecar_cols = [col for col in ("symbol", "metric", "value", "unit", "method", "as_of", "provider") if col in frame.columns]
    return _save(fig, run_dir / "charts" / "etf-premium.png", frame[sidecar_cols])


def _valuation_band(run_dir: Path) -> Path:
    path = run_dir / "analysis" / "percentile-series.csv"
    if not path.exists():
        raise FileNotFoundError("No percentile series found; run percentile first.")
    frame = pd.read_csv(path)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["multiple"] = pd.to_numeric(frame["multiple"], errors="coerce")
    frame = frame.dropna(subset=["date", "multiple"])
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for symbol, group in frame.groupby("symbol"):
        ax.plot(group["date"], group["multiple"], label=str(symbol))
    ax.set_title("Historical Valuation Multiple"); ax.set_xlabel("Date"); ax.set_ylabel("Multiple (x)"); ax.grid(True, alpha=0.25)
    if frame["symbol"].nunique() > 1:
        ax.legend()
    return _save(fig, run_dir / "charts" / "valuation-band.png", frame)


def _event_returns(run_dir: Path) -> Path:
    path = run_dir / "analysis" / "event-study.csv"
    if not path.exists():
        raise FileNotFoundError("No event-study output found; run event-study first.")
    frame = pd.read_csv(path)
    value_col = "abnormal_return_pct" if frame["abnormal_return_pct"].notna().any() else "raw_return_pct"
    plot = frame.dropna(subset=[value_col]).copy()
    if plot.empty:
        raise ValueError("No plottable event returns.")
    plot["label"] = plot["event_id"].astype(str) + " / " + plot["symbol"].astype(str) + " / " + plot["window"].astype(str)
    fig, ax = plt.subplots(figsize=(10, max(4.5, len(plot) * 0.35)))
    ax.barh(plot["label"], plot[value_col]); ax.axvline(0, linewidth=0.8)
    ax.set_title("Event Returns"); ax.set_xlabel("Percentage points"); ax.grid(True, axis="x", alpha=0.25)
    return _save(fig, run_dir / "charts" / "event-returns.png", plot)


def generate_chart(run_dir: str | Path, preset: str, metric: str | None = None) -> Path:
    configure_fonts()
    run_dir = Path(run_dir)
    if preset == "price-history":
        return _price_history(run_dir, False)
    if preset == "normalized-performance":
        return _price_history(run_dir, True)
    if preset == "metric-comparison":
        if not metric:
            raise ValueError("metric-comparison requires --metric")
        return _metric_comparison(run_dir, metric)
    if preset == "etf-premium":
        return _etf_premium(run_dir)
    if preset == "valuation-band":
        return _valuation_band(run_dir)
    if preset == "event-returns":
        return _event_returns(run_dir)
    raise ValueError("Unknown chart preset; choose price-history, normalized-performance, metric-comparison, etf-premium, valuation-band, or event-returns")
