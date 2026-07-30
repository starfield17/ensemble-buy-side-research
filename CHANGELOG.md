# Changelog

## 0.3.0 — merged research rigor and engineering workflow

### Architecture

- Unified the two v0.2 implementations into the installable `ensemble_research` package.
- Adopted a lightweight DDD split: domain calculations, application workflows, infrastructure connectors, presentation, and validation.
- Kept Python 3.13 + Conda, Typer CLI, deterministic offline demo, run directories, manifests, and structured source failures.

### Objective metrics

- Unified metric provenance: method, formula, raw inputs, provider, source dataset, date, currency, fiscal window, adjustment policy, status, `not_meaningful`, and caveats.
- Added PE TTM, PE ex-items, static PE, forward PE, PB, PS, EV/EBITDA (including minority interest where available), FCF yield, ROE, debt/equity, gross and operating margin.
- Kept explicitly labelled historical-3y, historical-5y, and forward-consensus PEG; added optional analyst-supplied custom PEG.
- Added period return, annualized volatility, maximum drawdown, historical valuation percentile, ETF NAV/IOPV premium, and event studies with raw, market-adjusted, or market-model returns.

### Data and output

- Kept yfinance, AKShare, Tushare, SEC EDGAR, and GDELT connectors with structured partial/failure records.
- Tushare no longer maps total liabilities to total debt. TTM fields are produced only when four compatible quarterly observations can be reconstructed; otherwise fields remain unavailable and notes explain why.
- Charts now write sidecar CSV files containing the exact plotted data.
- Added run validation with metric recomputation, artifact validation/rendering, and a `doctor` command.

### Research framework

- Retained the richer value-chain/profit-pool/quality/consensus/variant-view/falsification methodology, schemas, starter templates, worked example, and eval fixtures.
- Removed duplicated framework ownership: each detailed concept has one documentation file; `SKILL.md` acts as the router and hard-constraint contract.

### Compatibility

- Main CLI: `ensemble-research`.
- Compatibility alias: `buy-side-data`.
