# Advanced packaging capacity for AI accelerators

> **Illustrative example.** Every figure below is synthetic, produced from the fixture data in
> `tests/fixtures/`, and is here to show the expected shape and standard of a memo — not
> to describe any real company. Note that the judgment lands on `B. Watch`: a memo that always
> concludes `Deep Dive` is a memo whose judgment step is not working.

## Trigger

| Field | Answer |
|---|---|
| Trigger | Two foundry customers disclosed multi-year prepayments for packaging capacity |
| Trigger type | Supply / Capacity |
| Why now | Prepayment terms are new; previously capacity was allocated quarter to quarter |
| Real variable changed? | Yes — the contracting mechanism, which changes who bears utilization risk |

## Problem Solved

Accelerator performance is increasingly limited by how fast data moves between compute and memory
rather than by transistor density. Advanced packaging is what physically shortens that path. The
buyer — a chip designer — pays because without it a die that is otherwise finished cannot be
shipped at competitive bandwidth. The measurable improvement is bandwidth per package and yield at
assembly; the commercial consequence is that packaging capacity, not wafer capacity, sets the
shipment ceiling.

## Facts

| Fact | Source | Label |
|---|---|---|
| Two customers signed multi-year capacity prepayments | fixture: filing_2026Q1 | Fact |
| Prepayment shifts utilization risk from supplier to customer | — | Interpretation |
| If prepayments persist, supplier margin should be less cycle-sensitive than history implies | — | Hypothesis |
| Whether pricing is fixed or indexed within those contracts | — | Unknown. Source needed |

## Value Chain Map

| Layer | Problem solved by layer | Representative players | Bottleneck | Profit pool quality | Competition | Commoditization risk | Judgment |
|---|---|---|---|---|---|---|---|
| Interposer substrates | Carries high-density interconnect between dies | Alpha Components | high | high | low | low | Capacity is the binding constraint; pricing evidence supports genuine scarcity |
| Assembly capacity | Bonds compute and memory at yield | Alpha Components, Beta Systems | high | high | medium | low | Where the prepayments landed; the layer being repriced |
| Test and burn-in | Screens defects before high-value integration | Beta Systems | medium | medium | medium | medium | Necessary but historically price-taking |
| Equipment | Supplies bonders and inspection tools | Gamma Integrators | medium | unknown | high | medium | Order-driven and lumpy; economics unproven — see n.m. below |
| Materials | Supplies underfill, films, and carriers | not established | low | low | high | high | Many suppliers, standardized output |

## Profit Pool

- **Highest quality:** assembly capacity. Gross margin has held while volumes rose, which is the
  widening-moat signature rather than a scarcity artifact.
- **Most obvious but crowded:** the same layer. PE (TTM, diluted, as of 2026-05-15) is 36.1x for
  Beta Systems against a 5-year median of 22.4x — the market has already noticed.
- **Hidden / second-order:** interposer substrates, where the constraint originates but which
  attracts less coverage.
- **Likely pass-through:** materials.

## Quality Lens

| Field | Assessment | Evidence |
|---|---|---|
| Circle of competence | edge | Process economics are legible; customer roadmap timing is not |
| Business quality | strong | Margin stability through a volume ramp |
| Moat source | Process know-how plus capacity scarcity | Yield gap versus second-source attempts |
| Moat trend | unknown | Prepayments are too recent to distinguish structure from cycle |
| Pricing power | Present but possibly contractual | Unknown whether contracts fix or index price — decisive |
| Capital intensity | High | Capacity additions precede revenue by 4–6 quarters |
| Management / capital allocation | Unknown | Source needed |
| Five-year closure test | Not passed | Depends on whether the bottleneck stays at this layer |
| Downside / ruin risk | Moderate | Capex is committed ahead of demand; no leverage red flag found |
| Implication | **downgrade** | Moat trend unknown + valuation at the 88th percentile |
| Evidence still needed | Contract pricing mechanism; competitor qualification timelines | |

## Commoditization Risk

Test and burn-in is the layer most likely competed away: the output is standardized and customers
can qualify second sources within roughly four quarters. Assembly is protected for as long as
yield gaps persist, but that is a claim about the present, not a durable one — the survivors are
whoever holds the yield lead when the current capacity wave lands.

## Market Consensus

The story is straightforward and widely repeated: packaging is the bottleneck, therefore packaging
suppliers capture the economics. Crowding evidence is direct — Beta Systems trades at the 88th
percentile of its own 5-year PE range (window 2021-06 to 2026-05, 1,258 observations), and the
two most-cited beneficiaries have re-rated together. *Positioning data are not available; this is
inferred from valuation percentile and price action, not from flows.*

## Variant View

The market is right that the bottleneck is real and wrong about who absorbs its normalization.
Consensus prices assembly capacity as a durable profit pool; the prepayment structure suggests the
opposite reading — customers accepting utilization risk is what a supplier concedes when it
expects capacity to loosen. If so, the durable pool sits upstream in interposer substrates, where
qualification cycles are longer, rather than in assembly.

Layer: interposer substrates. Horizon: 12–24 months. Measurable via substrate lead times and
assembly utilization disclosed quarterly.

## Key Variables

Substrate lead times · assembly utilization rate · packaging ASP per unit · prepayment balance on
the balance sheet · competitor qualification announcements · gross margin at the assembly segment.

## Data Watchlist

| Variable | Why it matters | Source | Frequency | Bullish threshold | Bearish threshold | Current reading | Next check |
|---|---|---|---|---|---|---|---|
| Substrate lead time | Direct test of where the constraint sits | Supplier calls, industry data | Quarterly | Extends beyond 26 weeks | Falls below 16 weeks | Source needed | Next results |
| Assembly utilization | Distinguishes structural tightness from ramp | Company disclosure | Quarterly | Above 90% for 2 cycles | Below 80% | Source needed | Next results |
| Packaging ASP | Separates pricing power from volume | Segment disclosure | Quarterly | Flat-to-up with volume | Down while volume rises | Source needed | Next results |
| Prepayment balance | Shows whether customers keep committing | Balance sheet | Quarterly | Grows with capacity | Flat or drawn down | Source needed | Next results |

**Status rules** — Upgrade if lead times extend while ASPs hold for two cycles. Downgrade if
utilization falls below 80% with capacity still arriving. Abandon if ASPs decline while volumes
rise, which would confirm the pass-through reading.

## Initial Judgment

**B. Watch**

The problem is real and the bottleneck is evidenced, but the two things that would make this a
thesis are both unresolved: whether pricing is contractually fixed (which decides if margin is
durable or borrowed) and whether the moat is widening or merely tight. Valuation at the 88th
percentile removes the margin for being early. Watch rather than Deep Dive because the decisive
disclosure arrives next quarter, and committing research time before it is unnecessary.

## Falsification Conditions

1. Assembly ASPs decline for two consecutive quarters while unit volumes rise — the pass-through
   reading is correct and the profit pool is not durable.
2. A second supplier is qualified by a top-three customer within four quarters, confirming the
   yield gap is closing.
3. Prepayment balances flatten or are drawn down while capacity additions continue, indicating
   customers no longer expect scarcity.
4. Substrate lead times compress below 16 weeks while assembly utilization stays high, which would
   place the bottleneck at assembly after all and invalidate the upstream variant view.

## Next Research Steps

1. Read the contract terms disclosure in Alpha Components' next 10-Q for pricing mechanism.
2. Build a segment gross-margin table across the three named suppliers for eight quarters.
3. Track competitor qualification announcements from the top three accelerator customers.
4. Recompute the PE percentile after next results, with the same 5-year window, to check whether
   crowding is easing.
5. Establish who supplies interposer substrates — the variant view currently rests on one
   unnamed player, which is a gap.

---

*Research artifact, not investment advice. All figures in this example are synthetic.*
