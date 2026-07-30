# Data Sources

## Routing policy

With `--provider auto`:

- Mainland China price history: AKShare.
- Mainland China fundamentals: Tushare when `TUSHARE_TOKEN` is available; otherwise yfinance is attempted as a best-effort fallback.
- Non-mainland price history and fundamentals: yfinance.
- Mainland China ETF snapshot/IOPV: AKShare.
- Other ETF market price/NAV snapshot: yfinance.
- US filing metadata: SEC EDGAR.
- News metadata: GDELT.

Every connector records `success`, `partial`, `failed`, or `unsupported` in `manifest.json`. An empty response is never treated as proof that no data exist.

## Credentials and settings

```text
SEC_USER_AGENT                       Required for SEC; include a contact email.
TUSHARE_TOKEN                        Required for Tushare fundamentals.
ENSEMBLE_RESEARCH_REQUEST_TIMEOUT    Optional seconds; default 20.
ENSEMBLE_RESEARCH_CACHE_DIR          Reserved cache path.
```

The older `BUY_SIDE_REQUEST_TIMEOUT` variable remains a fallback for compatibility.

## Provider notes

### yfinance

Supplies adjusted price history and a current fundamentals snapshot. Fields may be sparse or change upstream. Forward EPS and long-term growth are estimates. The connector records partial status when the snapshot lacks enough usable fields.

### AKShare

Supplies mainland stock/ETF price history and current ETF snapshot data. Price history uses forward adjustment (`qfq`) where the endpoint supports it. ETF price, IOPV, NAV, and provider-reported premium fields can refer to different timestamps; the toolkit independently recomputes labelled premiums when inputs exist.

### Tushare

Supplies mainland fundamentals when permissions allow. Values reported in ten-thousand-CNY or ten-thousand-share units are converted to base units.

Important safeguards:

- Cumulative Chinese statements are converted into discrete quarters before a four-quarter TTM is reported.
- A value is not labelled TTM unless four compatible quarters are reconstructed.
- `total_liab` is **not** treated as interest-bearing debt. Debt is built from available borrowing/bond/current-maturity fields; missing components are disclosed.
- EPS may be derived from attributable TTM income divided by latest shares and is explicitly noted as not provider-reported diluted EPS.

### SEC EDGAR

Fetches filing metadata and links. It does not claim to normalize raw XBRL into audited TTM statements; period/dimension reconciliation remains a specialized task.

### GDELT

Collects news metadata only. The toolkit does not infer sentiment, consensus, catalysts, or investment conclusions from headlines.

## Known limitations

- Provider APIs and field names can change independently.
- Currency conversion is not automatic.
- Cross-listed securities may need manual symbol normalization.
- yfinance fundamentals are primarily current snapshots rather than restatement-aware point-in-time histories.
- Tushare permissions vary by account and endpoint.
- ETF IOPV/NAV timestamps and underlying-market sessions can differ materially.
- Live connectors are optional; `ensemble-research demo` is deterministic and offline.
