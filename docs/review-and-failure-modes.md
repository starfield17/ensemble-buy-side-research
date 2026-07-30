# Failure Modes

Run this as a self-audit before delivering. Each entry is a symptom you can check for in your own
draft, followed by the fix.

## Analysis failures

**1. Theme addiction.** The memo describes how large the opportunity is but not who captures
profit. → Force the value-chain and profit-pool sections before any company conclusion.

**2. Stock list instead of value chain.** Companies listed without layer or economics. → Map every
company to a layer and a role, or cut it.

**3. Consensus omission.** A thesis with no statement of what the market already believes. → Add
Market Consensus before Variant View.

**4. Fake contrarianism.** "The market is wrong" without a measurable disagreement. → Require a
variable, a time horizon, and a falsification condition.

**5. Revenue equals profit fallacy.** Growth assumed to mean good economics. → Check margin,
bargaining power, capex, competition.

**6. Ignoring losers.** Only beneficiaries listed. → Add potential losers and substitution effects.

**7. No time horizon.** → Separate 1–3 months, 3–12 months, 1–3 years.

**8. No watchlist.** A view with no way to track it. → Build the variable table with sources and
thresholds.

**9. No decision.** Information without judgment. → End with A/B/C/D and next steps.

## Evidence failures

**10. Unsupported current facts.** Claims about consensus, price, or guidance without
verification. → Label as assumption or `Source needed`, with the date of what you do know.

**11. Naked numbers.** A multiple reported without method, date, or currency; or metrics computed
different ways compared side by side. → Carry the method tag from the script output. If you cannot
state how a number was computed, do not use it.

**12. Invented precision.** A figure that a script would have produced, but no script was run. →
Either run it or mark `Source needed`. Never estimate into the gap.

**13. Regex-grade entities.** Company names or layer assignments that came from pattern matching
rather than a source. → Every named player needs a citation.

## Quality failures

**14. Moat label without evidence.** "Strong moat" with no pricing power, switching cost, cost
advantage, retention, or share evidence. → Fill the quality-lens block with numbers or mark
`Unknown`.

**15. Cheapness substituting for quality.** The thesis rests on a low multiple while the business
has weak returns or deteriorating economics. → Classify as cigar butt / turnaround / cyclical
trade, define catalyst and exit, and do not call it durable.

**16. Outside-the-circle confidence.** A confident conclusion on decisive variables you cannot
underwrite. → Mark competence as Edge or Outside, downgrade, list the specific unknowns.

**17. Small upside, fatal downside.** Modest upside with leverage, liquidity, governance,
refinancing, or tail risk. → Apply the ruin-risk override and downgrade.

## Process failures

**18. Score creep.** Composite scores, rankings, weighted indices, or "investability" numbers
appearing anywhere in the output or in the scripts. → Delete them. Judgment goes in prose with
evidence attached. This is the failure mode this skill was rebuilt to eliminate; watch for it
returning as a "quick summary table".

**19. Generic sell-side tone.** "Broad prospects", "expected to develop rapidly". → Rewrite into
problem, economics, variables, falsification.

**20. Template output.** The memo would read nearly the same for a different direction. → If
swapping the direction name leaves the text intact, no research happened. Rewrite with
direction-specific facts.

**21. Forced action.** Every memo concludes Deep Dive or Thesis. → `Watch` and `Discard` are real
answers. If you have not produced one recently, you are probably grading generously.

---

## Bounded subagent reviews

Use subagents only for independent qualitative critique; scripts remain responsible for deterministic calculations. Good bounded passes are value-chain review, profit-pool critique, consensus-vs-variant attack, watchlist/falsification review, and final memo red-team.

Give each reviewer the relevant artifacts and require:

```text
Findings:
Evidence Used:
Unverified Claims:
Suggested Changes:
Confidence:
```

Require `Fact` / `Interpretation` / `Hypothesis` / `Unknown` labels. Do not delegate “analyze this industry” or accept a subagent’s A/B/C/D judgment as authority.

Reconciliation rules:

- verify findings against source artifacts before accepting them;
- prefer filings, regulators, exchange notices, and company IR over secondary summaries;
- keep contradictory evidence visible;
- mark unresolved claims `Source needed` or `Unknown`;
- never paste reviewer prose without checking evidence and tone.
