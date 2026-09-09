---
name: ensemble-buy-side-research
description: "Harness-neutral buy-side research framework plus deterministic data toolkit. Use it to turn a theme, event, company, industry chain, peer set, or ETF into an auditable research pack: fetch market/fundamental/filing/news data, compute objective metrics (PE, PB, PS, PEG variants, EV/EBITDA, margins, returns, volatility, drawdown, historical valuation percentiles, ETF premium/discount, benchmark-adjusted event returns), generate tables/charts, validate artifacts, and then produce an analyst-authored value-chain, consensus, variant-view, watchlist, and falsification-based memo. Never use the scripts to score, rank, grade, or automatically recommend securities."
---

# Ensemble Buy-side Research

## Role

Convert a research trigger into a disciplined, source-backed buy-side research artifact. Think like a generalist deciding whether a direction deserves more work, not like a template-driven report generator.

Default question:

> What problem is solved, where is profit captured, what does the market already believe, where could a variant view exist, which observable variables validate or falsify it, and what should be researched next?

## Load-bearing boundary

> **Scripts only perform work that should produce the same answer for every analyst given the same inputs. All subjective judgments remain analyst-authored.**

Scripts may fetch, normalize, calculate, tabulate, chart, validate, and render supplied fields. Scripts must never:

- assign investment, moat, quality, profit-pool, or consensus scores;
- rank or grade companies/layers by attractiveness;
- infer a buy/sell/hold verdict;
- generate a memo narrative or fill missing analysis;
- choose an implicit growth assumption for a generic PEG;
- hide missing, stale, non-comparable, or non-meaningful data.

## Research flow

```text
Trigger → Problem Solved → Circle of Competence → Value Chain → Profit Pool
→ Quality Lens → Commoditization → Consensus → Variant View → Key Variables
→ Falsification → Initial Judgment → Next Research Action
```

Label important claims as `Fact`, `Interpretation`, `Hypothesis`, or `Unknown`. Write `Source needed` rather than inventing evidence.

## Output levels

Choose one and justify it:

- **A. Discard** — weak/untestable problem, no attractive profit pool, or unacceptable ruin risk.
- **B. Watch** — direction is real but timing, economics, or evidence is insufficient.
- **C. Deep Dive** — analyzable chain, plausible profit capturers, and a possible consensus gap.
- **D. Potential Investment Thesis** — durable economics, defensible player, plausible mispricing, and explicit validation/falsification variables.

A and B are valid outcomes.

## Required memo sections

```markdown
# Direction
# Trigger
# Problem Solved
# Facts
# Value Chain Map
# Profit Pool
# Quality Lens
# Commoditization Risk
# Market Consensus
# Variant View
# Key Variables
# Data Watchlist
# Initial Judgment
# Falsification Conditions
# Next Research Steps
```

## Installation

```bash
conda env create -f environment.yml
conda activate ensemble-buy-side-research
```

The package exposes both `ensemble-research` and the compatibility alias `buy-side-data`.

## Common commands

```bash
# deterministic offline end-to-end run
ensemble-research demo --output runs/demo

# live fetch + objective metrics + tables/charts + validation
ensemble-research run \
  --symbols AAPL,MSFT,510300.SS \
  --datasets prices,fundamentals,etf,filings \
  --start 2024-01-01 \
  --output runs/example

# individual stages
ensemble-research fetch --symbols AAPL,MSFT --datasets prices,fundamentals --output runs/example
ensemble-research metrics --run runs/example
ensemble-research table --run runs/example --preset valuation-comparison
ensemble-research chart --run runs/example --preset metric-comparison --metric pe_ttm
ensemble-research percentile --run runs/example --symbol AAPL --metric pe_ttm --lookback-years 5
ensemble-research event-study --run runs/example --events events.json --benchmark SPY --model market-adjusted
ensemble-research validate-run --run runs/example

# analyst-authored artifacts
ensemble-research validate-artifact --file value_chain.json --schema value_chain --strict
ensemble-research render-artifact --input value_chain.json --output value_chain.md
ensemble-research doctor
```

## Reading outputs

Always inspect `manifest.json` and `validation.json` first. Every metric record carries its method, raw inputs, provider, source dataset, date, currency, fiscal window, adjustment policy, status, and caveats.

- `status=valid`: calculable under the documented method.
- `status=unavailable`: required data is missing.
- `not_meaningful=true`: a quotient could be misleading, such as PE with non-positive earnings.
- Percent values are stored as percentage points: `6.5` means `6.5%`.
- Distinct method tags are distinct metrics; do not average them together.
- Cross-market tables require explicit accounting/currency/free-float caveats.
- Historical valuation percentiles are only as point-in-time as the supplied fundamentals.
- ETF NAV and IOPV premiums are different measurements and must remain labelled.

## Structured artifacts

The analyst or model authors `value_chain.json`, `thesis.json`, `watchlist.json`, `source_pack.json`, and `research_memo.json` using `schemas/` and `templates/`. The code only validates and renders supplied content.

## Documentation map

- `docs/research-method.md` — value chain, profit pool, quality lens, consensus, variant view, falsification.
- `docs/evidence-and-writing.md` — source hierarchy, claim labelling, citations, writing discipline.
- `docs/data-sources.md` — routing, credentials, coverage, limitations, and provider-specific caveats.
- `docs/metric-definitions.md` — formulas, units, required inputs, and non-meaningful conditions.
- `docs/output-contract.md` — run directory, manifest, dataset and metric schemas.
- `docs/review-and-failure-modes.md` — red-team review, subagent use, and delivery checks.

Read only the document needed for the current stage.

## Hard constraints

Do not present unsupported assumptions as facts; report a metric without its method/date/source; compare inconsistent methods; confuse cheapness with business quality; infer consensus from headlines alone; promote a thesis outside the circle of competence; ignore leverage, liquidity, governance, or ruin risks; or deliver a thesis without falsification.

This skill produces research artifacts, not personalized investment advice. Live outputs depend on provider availability and credentials.
