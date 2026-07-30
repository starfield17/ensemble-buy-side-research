# Output Contract

## Run directory

```text
run/
├── manifest.json
├── data/
│   ├── prices.*
│   ├── fundamentals.*
│   ├── etf_snapshot.*
│   ├── filings.*
│   ├── news.*
│   └── events.json                # optional analyst/demo input
├── metrics/
│   ├── metrics.*
│   └── metric_definitions.json
├── analysis/
│   ├── percentile-series.csv
│   ├── percentile.json
│   └── event-study.csv
├── tables/
├── charts/
│   ├── <chart>.png
│   └── <chart>.csv                # exact plotted data sidecar
└── validation.json
```

CSV is the default portable format. Parquet requires `pyarrow`.

## Manifest

`manifest.json` records tool/schema version, requested symbols/datasets, run status, artifact paths, source records, structured errors, and notes. Source states are `success`, `partial`, `failed`, and `unsupported`.

## Core data tables

- `prices`: requires `symbol`, `date`, `close`, `provider`; may include OHLCV, currency, and adjustment policy.
- `fundamentals`: requires `symbol`, `as_of`, `provider`; supports fiscal window, market/enterprise value, TTM fields, book value, debt, cash, minority interest, EPS variants, growth fields, and nulls for unavailable data.
- `etf_snapshot`: requires `symbol`, `as_of`, `market_price`, `provider`; may include timestamp, IOPV, NAV, cross-border flag, and provider-reported premium.
- `filings` and `news`: source-material metadata only; not scored or interpreted.

## Metric table

Each row contains:

```text
symbol, metric, value, unit, method, formula, inputs,
as_of, fiscal_window, currency, provider, source_dataset,
adjustment_policy, status, not_meaningful, caveats
```

`inputs` and `caveats` are JSON strings in CSV output.

## Tables and charts

Tables retain method tags and caveats. Metric-comparison charts preserve input order rather than sorting by value, because sorting can visually imply an attractiveness ranking. Every chart has a sidecar CSV with the plotted series and available provenance.

## Analyst-authored artifacts

`schemas/` defines `value_chain`, `thesis`, `watchlist`, `source_pack`, and `research_memo`. The analyst/model authors their content. Code may validate placeholders/schema and render supplied fields, but never invent narrative.

## Validation

`validation.json` checks manifest shape, declared artifact existence, required columns, dates, duplicate prices, metric state consistency, and independent formula recomputation where raw inputs are sufficient. Validation confirms artifact mechanics, not thesis quality or investment suitability.
