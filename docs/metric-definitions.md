# Metric Definitions

## General contract

Every metric row stores `value`, `unit`, `method`, `formula`, raw `inputs`, `as_of`, `fiscal_window`, `currency`, `provider`, `source_dataset`, `adjustment_policy`, `status`, `not_meaningful`, and `caveats`.

- Percent values are percentage points: `6.5` means `6.5%`.
- `unavailable` means required inputs are absent.
- `not_meaningful=true` means a number would be financially misleading, such as PE with non-positive earnings.
- Different method tags are distinct observations and must not be silently averaged.
- No metric becomes a score, rank, grade, or investment verdict.

## Valuation and cash generation

| Metric | Method/formula | Main caveat |
|---|---|---|
| `pe_ttm` | market cap / TTM net income; fallback price / diluted TTM EPS | No meaningful PE for non-positive earnings. |
| `pe_ttm_ex_items` | price / diluted TTM EPS excluding non-recurring items | Provider definitions of recurring items differ. |
| `pe_static` | price / last full-year diluted EPS | Uses an older fiscal window. |
| `pe_forward` | price / forward consensus EPS | Estimate, not audited fact. |
| `pb` | market cap / common equity; fallback price / BVPS | No meaningful PB for non-positive book value. |
| `ps_ttm` | market cap / TTM revenue | Revenue recognition differs. |
| `ev_ebitda` | EV / TTM EBITDA | EV uses market cap + debt + minority interest − cash when reconstructed. Missing components are disclosed. |
| `fcf_yield` | TTM free cash flow / market cap × 100 | FCF may be provider-reported or OCF minus capex. |

## PEG variants

| Metric | Growth source |
|---|---|
| `peg_historical_3y` | explicitly labelled 3-year historical EPS CAGR |
| `peg_historical_5y` | explicitly labelled 5-year historical EPS CAGR |
| `peg_forward_consensus` | explicitly labelled provider/analyst long-term estimate |
| `peg_custom` | analyst-supplied `SYMBOL=RATE`; source and horizon must be cited in the memo |

Inputs `0.18` and `18` both normalize to 18 percentage points. PEG is unavailable when PE/growth is missing and not meaningful when growth is non-positive. The toolkit never chooses a generic “best” growth assumption.

## Profitability and leverage

| Metric | Formula |
|---|---|
| `roe` | TTM net income / common equity × 100 |
| `debt_to_equity` | interest-bearing total debt / common equity |
| `gross_margin` | TTM gross profit / TTM revenue × 100 |
| `operating_margin` | TTM operating income / TTM revenue × 100 |

## Price-series statistics

| Metric | Formula |
|---|---|
| `period_return` | `(last close / first close − 1) × 100` |
| `annualized_volatility` | sample standard deviation of daily returns × √252 × 100 |
| `max_drawdown` | minimum `(close / running peak − 1) × 100` |

These describe the supplied window; they are not forecasts.

## Historical valuation percentile

`percentile` backward-joins each trading date to the most recent prior supplied fundamental observation and supports `pe_ttm`, `pb`, and `ps_ttm`. Output includes requested/actual lookback, observation count, distribution quartiles, and a standing point-in-time/restatement caveat. Fewer than 60 valid observations is flagged unreliable.

## ETF premium/discount

| Metric | Formula |
|---|---|
| `premium_to_iopv` | `(market price / IOPV − 1) × 100` |
| `premium_to_nav` | `(market price / official NAV − 1) × 100` |

Positive is premium; negative is discount. IOPV is estimated/intraday. Cross-border funds can retain apparent dislocations because of time zones, FX, quotas, and creation/redemption constraints.

## Event study

Windows are trading-day offsets and include the return on the anchor session. Non-trading-day events anchor to the next session and record that choice.

- `raw`: compounded security return.
- `market_adjusted`: security return minus benchmark return.
- `market_model`: pre-event OLS alpha/beta expectation; falls back to market-adjusted when estimation history is insufficient.

Outputs are percentage points and remain descriptive evidence, not causal proof.
