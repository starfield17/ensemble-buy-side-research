# Evidence and Style

Merged from the old evidence policy and style guide. Single source for source grading, the
fact/interpretation/hypothesis triad, and prose rules.

## Part 1 — Evidence

### Classify every important input

```text
Primary evidence · Secondary evidence · Market evidence · Management claim
Model output · User-provided assumption · Unverified claim
```

### Fact / Interpretation / Hypothesis

```text
Fact:           Company X disclosed Y revenue in segment Z. (source, date)
Interpretation: Segment growth suggests adoption is improving, but margin impact is not visible.
Hypothesis:     If adoption continues, layer-A suppliers should show backlog growth within
                two reporting cycles.
Unknown:        Whether the customer is single-sourcing. Source needed.
```

Use these labels consistently. A statement may not appear as a conclusion unless labeled or
clearly supported.

### Source reliability

| Source type | Weight |
|---|---|
| Primary filing / annual report / 10-K / 10-Q | Highest |
| Earnings-call transcript | Highest |
| Regulator or government statistical source | Highest |
| Exchange announcement | Highest |
| Company investor presentation | High, but promotional |
| Reputable financial media | High |
| Industry association | Medium-high |
| Sell-side report | Medium — useful mainly as evidence of consensus |
| Expert interview | Medium-high, single-source risk |
| Social media / forum | Low |
| Unsourced claim | None — do not use |

These are relative weights for your judgment, not scores to be totaled.

Be cautious with anonymous claims, aggregated SEO pages, promotional decks, and single-source
rumors.

### Source pack fields

`Title` · `URL or local reference` · `Source type` · `Publisher` · `Date` · `Reliability` ·
`Relevant claims` · `Linked variables`

Conforms to `schemas/source_pack.schema.json`.

### Handling unknowns

Write `Unknown:`, `Source needed:`, or `Assumption:`. Do not fill gaps with confident language.
A memo with visible gaps is more useful than one with invisible ones.

### Freshness

Prices, multiples, guidance, management, policy, and capacity plans go stale fast. Before treating
any of these as current fact, verify via scripts or web access. If you cannot, label it and give
the date of the information you do have.

### Evidence-to-thesis chain

Every thesis should be traceable:

```text
Source → Fact → Interpretation → Hypothesis → Variable → Falsification
```

If you cannot walk a claim back to a source, it is a hypothesis — label it as one.

### Contradictory evidence

Do not hide it:

```text
Supporting evidence:
Contradictory evidence:
Which side matters more, and why:
What data would resolve it:
```

### Minimum evidence by judgment level

| Level | Requires |
|---|---|
| A. Discard | Enough evidence to show the problem or economics are weak |
| B. Watch | A plausible problem, insufficient evidence on timing, economics, or consensus |
| C. Deep Dive | Evidence of a real problem and a possible profit pool |
| D. Thesis | Clear support for problem, profit pool, variant view, variables, and falsification |

## Part 2 — Style

### Voice

Direct · skeptical · specific · decision-oriented · comfortable with uncertainty.

Avoid promotional language, generic optimism, sell-side neutral padding, unfalsifiable claims,
and academic framing.

### Good sentences

> The problem is real, but the investable layer is not obvious yet.

> The market appears to be paying for hardware scarcity, while the more durable profit pool may
> sit in software control and lifecycle services.

> This is a watchlist item, not yet a thesis, because the key variable is still customer adoption
> rather than supply availability.

> The obvious beneficiary may be crowded; the second-order beneficiary is the supplier whose
> margin expands when the bottleneck persists.

### Bad sentences

> This industry has broad development prospects.

> The company will fully benefit from the trend.

> The market does not understand this at all.

> This is a long-term opportunity with huge potential.

### Formatting

Short paragraphs. Tables for value-chain maps, watchlists, and peer comparisons. Bullets for
falsification, next steps, risks, and assumptions. Explicit labels for facts and assumptions.

Avoid long background sections, history not tied to current economics, unstructured company
lists, and generic SWOT.

### Reporting numbers

Always carry the method tag from the scripts: "PE (TTM, diluted, as of 2026-06-30) 31.4x", not
"PE 31.4". State the currency for cross-market comparisons. When a metric is
`not_meaningful`, say so and explain why rather than printing the raw number.

Prefer "82nd percentile over 5 years" to "expensive". Prefer "gross margin fell 340bp over four
quarters" to "margins are under pressure".

### No imitation rule

The style may be inspired by a problem-first, value-chain-driven buy-side memo format. Do not
impersonate any specific author. Internalize the analytical structure, not a personal voice.
