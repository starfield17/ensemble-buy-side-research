# Research Method

Single authoritative source for the research pass: principles, control flow, and per-step
mechanics. Quality/moat criteria and analytical checklists are consolidated in this document. Source grading and prose rules live in `evidence-and-writing.md`.

## Contents

1. [Principles](#principles)
2. [Control flow](#control-flow)
3. [Step mechanics](#step-mechanics)
4. [Quality Lens](#quality-lens)
5. [Analytical Checklists](#analytical-checklists)

---

## Principles

**1. Start with the problem, not the theme.** A theme is not investable by itself.

Weak: "Humanoid robots are a major future trend."
Strong: "Humanoid robots attempt to solve labor scarcity and automation flexibility where fixed
industrial automation is too rigid."

Every direction must answer: What is broken? Who pays to fix it? Why now? What variable improves
if it works?

**2. A direction is a value chain, not a stock list.** Upstream inputs, core components, systems
integration, software/control, distribution, customer application, aftermarket. The first obvious
beneficiary is rarely the best profit pool.

**3. Profit pool comes before popularity.** Attention is not economics. Durable pools usually rest
on scarcity, a technical bottleneck, process know-how, a regulatory license, customer lock-in,
switching cost, data advantage, scale, or ecosystem control.

**4. Consensus must be explicit.** Never write a thesis without stating what the market likely
already believes. What is priced? What is not? What is priced wrongly?

**5. A variant view must be measurable.** It is not a personality trait. It must map to observable
data, a value-chain layer, a time horizon, and an error condition.

**6. Good research ends with a watchlist,** not just a memo — a monitoring system: *if variable X
crosses threshold Y, update thesis status.*

**7. Falsification protects against narrative addiction.** What would make you downgrade? Abandon?
What would show the market was right and you were wrong?

**8. Separate first- and second-order effects.** First-order: direct supplier to the demand shock.
Second-order: bottleneck provider, equipment vendor, infrastructure enabler, replacement-cycle
beneficiary — often where pricing power actually lands.

**9. Time horizon matters.** 1–3 months: narrative and positioning. 3–12 months: order, pricing,
margin evidence. 1–3 years: capacity, share shift, structural profitability.

**10. Buy businesses, not tickers.** Would this be attractive if you owned the whole business?
What cash earnings can it generate and reinvest? Do not justify a thesis with chart patterns,
headlines, or price targets alone.

**11. Time helps wonderful businesses and hurts poor ones.** Classify: compounder, cigar butt,
turnaround, cyclical trade, narrative proxy. A cheap weak business is not a compounder.

**12. Macro humility.** Macro may matter but is often unknowable. Prefer knowable business-level
variables: price, volume, margin, backlog, capacity, inventory, churn, retention, cash conversion.

**13. Inactivity is a valid outcome.** `Watch`, `Discard`, and `Source needed` are real
conclusions. The framework must not force action.

Circle-of-competence and moat principles are defined in the Quality Lens section below — they are gates on the
judgment, not general principles, and are stated there once.

---

## Control flow

```text
1.  Normalize input
2.  Classify trigger
3.  Define the problem solved
4.  Build preliminary value-chain map
5.  Identify players by layer
6.  Assess profit pools           → Analytical Checklists below
7.  Apply the quality lens        → Quality Lens below
8.  Assess commoditization risk   → Analytical Checklists below
9.  Extract or infer consensus    → Analytical Checklists below
10. Generate variant-view candidates, select the strongest
11. Convert the thesis into observable variables
12. Build the watchlist
13. Define falsification conditions
14. Assign the initial judgment (A/B/C/D)
15. Write 3–7 operational next steps
```

Steps 6–9 are where scripts help: valuation metrics, percentiles, ETF premium, and event returns
give you numbers to reason from. They do not produce the assessment.

### Standard inputs

`Direction` · `Trigger` · `Company` · `Region` · `Time horizon` · `Known sources` ·
`Existing view` · `Required output format`

If input is incomplete, proceed with best-effort assumptions and mark them explicitly.

### Default scope

Unless told otherwise, treat the universe as global but separate US/global leaders, China/domestic
substitution candidates, and other regional specialists. Do not merge them into one valuation
table without noting accounting, currency, and liquidity differences.

---

## Step mechanics

### 1. Normalize input

```text
Raw:  "AI inference and Broadcom maybe benefiting from hyperscaler custom chips"

Normalized:
  Direction:     AI inference accelerator ecosystem
  Company focus: Broadcom
  Trigger:       hyperscaler custom silicon adoption
  Region:        Global / US
  Time horizon:  6–24 months
```

### 2. Classify the trigger

One or more of: Demand · Supply · Policy · Technology · Financial · Narrative · Price action ·
Competitive · Customer adoption · Capacity.

Then answer: Why now? Who is affected first? Who second? **Is this a real variable change or only
a narrative refresh?**

Output a triage line: trigger type, affected direction, first-order beneficiaries, second-order
beneficiaries, potential losers, real variable changed (yes/no/unclear), priority.

### 3. Define the problem

```text
This direction exists because [customer/system] needs to reduce
[cost / latency / risk / scarcity / underpenetration] in [use case].
The buyer pays because ______.
The measurable improvement is ______.
```

Translate into economic variables: cost reduction, throughput, yield, latency, revenue unlock,
risk reduction, working capital, labor substitution, energy efficiency, compliance.

Score problem quality qualitatively against the Problem Quality checklist below → Problem Quality. Do not total it.

### 4. Value-chain map

One row per layer:

| Layer | Problem solved by layer | Representative players | Bottleneck | Profit pool quality | Competition | Commoditization risk | Judgment |

Standard starting layers (a prompt, not a template to fill blindly): raw materials · specialized
inputs · equipment/tools · core components · systems/integration · software/control ·
distribution/channels · customer application · services/aftermarket.

**Derive layers from the actual direction and its sources.** A generic layer list applied to a
specific industry is a tell that no research happened.

Every layer must help answer: who captures economics, who is replaceable, who is only a narrative
proxy. Never write it as an encyclopedia.

### 5. Player mapping

Separate core beneficiaries · derivative beneficiaries · narrative proxies · potential losers.
Every company must be mapped to a layer and a role. Never list companies without economics.

Naming a company is a factual claim. Cite where you got it; do not pattern-match tickers to
themes.

### 6–9. Profit pool, quality, commoditization, consensus

Work the Analytical Checklists and apply the Quality Lens below, then state:

```text
Highest-quality profit pool:
Most obvious but crowded pool:
Hidden or second-order pool:
Likely low-quality / pass-through layer:
```

For consensus, if you have no fresh market data, write `Assumed consensus, pending source
validation:` — do not pretend to know current positioning. Valuation percentiles and event
returns from the scripts are the strongest available evidence of what is already priced.

### 10. Variant view

A variant view must meet **all** of: it differs from consensus · it maps to a layer · it is
measurable · it has a time horizon · it has falsification conditions.

Valid shapes:

```text
Right direction, wrong layer.
Right demand, wrong margin capture.
Right leader, but second-order suppliers underestimated.
Early scarcity extrapolated into permanent pricing power.
A cyclical restocking cycle read as secular demand.
Market sees revenue; misses working-capital or margin risk.
Market sees technology; misses customer adoption friction.
```

Invalid: "This is a big opportunity." · "The market does not understand this." · "This company
will benefit from the trend."

Generate 1–3 candidates, then select the strongest and say why the others are weaker.

### 11. Key variables

Reduce the thesis to observables: price · volume · orders · backlog · gross margin · utilization ·
capacity · capex · inventory · lead time · take rate · ARPU · retention · attach rate · renewal ·
regulatory approval · technical benchmark · customer concentration.

Map: `Thesis driver → Observable variable → Source → Frequency → Threshold`.

### 12. Watchlist

| Variable | Why it matters | Source | Frequency | Bullish threshold | Bearish threshold | Current reading | Next check |

Where data are unavailable, write `Source needed` — never a guess. Thresholds should be specific
enough that someone else could check them without asking you.

### 13. Falsification

3–7 conditions. Specific:

> If hyperscaler capex grows but custom-silicon suppliers show no backlog or margin improvement
> within 2–3 reporting cycles, the thesis is weakened.

Not vague: "If the industry does not grow, the thesis is wrong."

Common shapes: demand slows while capacity expands · margins compress despite revenue growth ·
customers adopt open-source or in-house alternatives · the bottleneck shifts to another layer ·
policy support reverses · inventory builds ahead of sell-through · capex guidance is cut.

### 14. Initial judgment

Assign A/B/C/D per SKILL.md with 2–4 sentences of reasoning. Apply the overrides in
the Quality Lens judgment overrides below before finalizing.

### 15. Next steps

3–7 concrete actions: read filings · compare margins · map customers · build company list · track
variable · validate source · run event study · check valuation percentile · study substitute ·
interview expert.

Make each operational — name the document, the metric, or the company.

---

## Quality Lens

Owner-oriented quality and risk gate. Apply **after** profit-pool work and **before** the final
judgment. This file is the single authoritative source for circle of competence, moat criteria,
and the judgment overrides — they are not repeated elsewhere.

This section must be capable of changing the judgment. If it never downgrades anything, it is
decoration.

## 1. Circle of competence gate

```text
Inside:  economics, customers, competitors, and risks are understandable.
Edge:    analyzable, but one or two decisive variables need targeted research.
Outside: success depends on forecasting technology, macro, regulation, or competitive
         behaviour you cannot reasonably understand.
```

Inside ideas may proceed to thesis work. Edge ideas may become `Watch` or `Deep Dive` only if the
unknowns are explicitly listed and tracked. Outside ideas may not become
`Potential Investment Thesis`, however attractive the narrative.

The size of the circle matters far less than knowing its boundary.

## 2. Business ownership test

Analyze the security as ownership in a business, not a ticker or a catalyst.

```text
What would I earn if I owned the whole business?
How much incremental capital is required to grow?
Are profits cash-like or accounting-like?
Who holds bargaining power: company, customers, suppliers, or regulators?
```

Prefer recurring demand · high return on incremental capital · low capital intensity relative to
growth · pricing power · customer trust or habit · a long runway without constant reinvention.

Avoid low-return businesses bought only because they look cheap · capital-intensive growth with
poor incremental returns · revenue growth that leaks to customers, suppliers, or competitors.

## 3. Moat and moat trend

A moat is not a slogan; it must appear in evidence. **Moat trend matters more than moat label.**

Sources: brand / share of mind · low-cost position · network or ecosystem effects · switching cost
· distribution advantage · scale procurement or scale data · process know-how · regulatory license
· scarce asset or location.

| Widening evidence | Narrowing evidence |
|---|---|
| Stable or rising gross margin despite competition | Price promotion becomes necessary |
| Improving retention or repeat purchase | Substitutes gain credibility |
| Rising share without discounting | Customers multi-source or self-build |
| Lower unit cost versus peers | Gross margin falls while revenue rises |
| Customers pay a premium willingly | Supplier count grows faster than demand |
| Competitors fail despite capital access | Brand loses share of mind |

Most of the left column is checkable with `ensemble-research metrics` output plus filings.
Cite the number, not the adjective.

## 4. Quality before cheapness

```text
Cigar butt:  one-time value realization, weak business, limited reinvestment runway.
Compounder:  durable business, strong incremental returns, long reinvestment runway.
Turnaround:  requires operational change; speculative until evidence appears.
```

A cheap weak business can be `Watch` or a tactical `Deep Dive`, but should rarely be
`Potential Investment Thesis` unless the catalyst, downside, and exit are all explicit.

A low valuation percentile is a starting question, not an answer. Cheap relative to its own
history is often correct repricing of deteriorating economics.

## 5. Five-year market closure test

> If the exchange closed for five years, would I be comfortable owning this business on its
> economics, balance sheet, and competitive position alone?

If the answer depends mainly on near-term price action, sentiment, or multiple expansion,
downgrade the judgment.

## 6. Downside and ruin risk

Never risk what matters for what does not. Treat leverage, refinancing, customer concentration,
regulatory cliffs, and governance/fraud risk as thesis-level issues, not footnotes.

Red flags: the thesis requires leverage to work · liquidity depends on friendly capital markets ·
small upside with existential downside · management incentives reward growth over returns ·
opaque or off-balance-sheet exposure · a model whose output hides tail risk.

## 7. Output block

Every full memo includes:

```text
Circle of competence: inside / edge / outside / unknown
Business quality:     weak / mixed / strong / exceptional
Moat source:
Moat trend:           widening / stable / narrowing / unknown
Owner economics:
Pricing power:
Capital intensity:
Management / capital allocation:
Five-year market closure test:
Downside / ruin risk:
Quality-lens implication: upgrade / neutral / downgrade / pass
Evidence still needed:
```

Each line is either evidence-backed or marked `Unknown` / `Source needed`. A block of confident
adjectives with no numbers behind it is worse than an honest `Unknown`.

## 8. Judgment overrides

These override the rest of the analysis:

```text
Outside circle of competence            → cannot be Potential Investment Thesis.
No durable moat + high commoditization  → normally Watch or Discard.
High leverage or ruin risk              → downgrade regardless of upside.
Wonderful business, no valuation sanity → Watch until price/risk-reward is clear.
Wonderful business + measurable consensus gap + valuation sanity → Deep Dive or Thesis.
```

"Valuation sanity" means you looked at the multiple and its historical percentile and can state
what has to be true for the price to make sense — not that the number felt acceptable.

---

## Analytical Checklists

> **These are thinking prompts, not a scoring system.** Do not assign numbers, do not total them,
> do not compare totals across directions or companies. The previous version of this skill
> compiled these dimensions into an "investability score" that turned out to be a constant with
> arithmetic wrapped around it. Work each dimension, state a position in words, and cite the
> evidence behind it.
>
> The useful output of a checklist is a sentence like "pricing power is weak — ASPs fell 12% while
> volumes rose, so the demand growth is leaking to customers," not a 3 out of 5.

## Problem quality

| Dimension | Weak | Strong |
|---|---|---|
| Urgency | Nice-to-have | Mission-critical |
| Recurrence | One-off | Continuous |
| Budget owner | Unclear who pays | Identified buyer with budget |
| Measurability | Vague benefit | Directly measurable improvement |
| Switching incentive | Weak | Strong economic reason to change |

If most dimensions land weak, the direction is a theme, not an investable problem.

## Profit pool

| Dimension | Weak | Strong | Where to check |
|---|---|---|---|
| Gross margin potential | Commodity | Structurally high | `ensemble-research metrics`, filings |
| Pricing power | Price taker | Price setter | ASP trend vs volume trend |
| Switching cost | Low | High | Contract terms, retention disclosures |
| Supply scarcity | Abundant | Constrained | Capacity announcements, lead times |
| IP / know-how barrier | Low | High | Patents, yield gaps, hiring patterns |
| Customer concentration | Severe | Diversified | 10-K customer disclosure |
| Capex burden | Heavy, weak returns | High return on capital | Capex vs incremental operating profit |
| Operating leverage | Low | High | Incremental margin across quarters |
| Cycle risk | High | Low | Peak-to-trough margin history |
| Regulatory barrier | None | Meaningful protection | Licensing regime |

Then state:

```text
Highest-quality profit pool:
Most obvious but crowded pool:
Hidden or second-order pool:
Likely low-quality / pass-through layer:
```

## Commoditization risk

Warning signs — the more present, the more likely the layer is competed away:

```text
Standardized output            Many suppliers
Customer self-build            Open-source substitution
Low switching cost             Aggressive capacity additions
Declining ASP                  Weak differentiation
Price transparency             Policy-driven overinvestment
Capital intensity without differentiation
Inventory build ahead of sell-through
```

State: which layer is at risk, why, over what timeline, who survives, and the investment
implication.

## Consensus gap

| Dimension | Weak gap | Strong gap |
|---|---|---|
| Narrative clarity | Market has no clear story | Very clear, repeated story |
| Evidence of crowding | None | Strong (valuation percentile, flows, price action) |
| Misunderstood variable | None identified | A specific variable is misread |
| Timing mismatch | None | Market is pricing the wrong horizon |
| Layer mispricing | None | Market is paying for the wrong layer |

A weak gap does not mean a bad company — it means a weak *variant perception*, which is a
different conclusion. Say which one you mean.

Valuation percentile output is the most objective crowding evidence available to you. Use it
rather than asserting that something "feels extended".

## Thesis readiness

Do not label a direction `Potential Investment Thesis` unless every line is true:

```text
[ ] The problem is specific and economic.
[ ] The value-chain layer is identified.
[ ] The profit pool is credible and evidenced.
[ ] The consensus is stated.
[ ] The variant view is testable.
[ ] Key variables are observable, with sources.
[ ] Falsification conditions are explicit.
[ ] The next research action is concrete.
[ ] The quality lens forces no downgrade: inside or edge of competence, moat evidence present,
    no ruin risk, and valuation sanity checked against a percentile.
[ ] Every number in the memo carries its method tag and date.
```
