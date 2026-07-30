from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from ...models import SourceRecord
from .common import failed_source

PROVIDER = "sec"
SEC_BASE = "https://data.sec.gov"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"


def _get_json(url: str, user_agent: str, timeout: int) -> dict[str, Any]:
    response = requests.get(url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def ticker_map(user_agent: str, timeout: int) -> dict[str, str]:
    payload = _get_json("https://www.sec.gov/files/company_tickers.json", user_agent, timeout)
    return {str(item["ticker"]).upper(): str(item["cik_str"]).zfill(10) for item in payload.values()}


def fetch_filings(symbols: list[str], user_agent: str | None, timeout: int = 20, limit: int = 12) -> tuple[pd.DataFrame, list[SourceRecord]]:
    if not user_agent:
        return pd.DataFrame(), [failed_source(PROVIDER, "filings", "SEC_USER_AGENT not set", missing=["SEC_USER_AGENT"])]
    try:
        mapping = ticker_map(user_agent, timeout)
    except Exception as exc:
        return pd.DataFrame(), [failed_source(PROVIDER, "filings", str(exc), exc=exc)]
    rows: list[dict[str, object]] = []
    records: list[SourceRecord] = []
    for symbol in symbols:
        ticker = symbol.split(".")[0].upper()
        cik = mapping.get(ticker)
        if not cik:
            records.append(SourceRecord(provider=PROVIDER, dataset="filings", symbol=symbol, status="unsupported", notes=["No SEC CIK mapping; symbol may be outside SEC coverage."]))
            continue
        try:
            payload = _get_json(f"{SEC_BASE}/submissions/CIK{cik}.json", user_agent, timeout)
            recent = payload.get("filings", {}).get("recent", {})
            count = 0
            for idx, form in enumerate(recent.get("form", [])):
                if form not in {"10-K", "10-Q", "20-F", "6-K", "8-K"}:
                    continue
                accession = recent["accessionNumber"][idx]
                accession_compact = accession.replace("-", "")
                primary_doc = recent["primaryDocument"][idx]
                rows.append(
                    {
                        "symbol": symbol,
                        "company": payload.get("name") or ticker,
                        "form": form,
                        "filing_date": recent["filingDate"][idx],
                        "report_date": recent["reportDate"][idx],
                        "accession": accession,
                        "url": f"{SEC_ARCHIVES}/{int(cik)}/{accession_compact}/{primary_doc}",
                        "provider": PROVIDER,
                    }
                )
                count += 1
                if count >= limit:
                    break
            records.append(SourceRecord(provider=PROVIDER, dataset="filings", symbol=symbol, status="success" if count else "partial", record_count=count))
        except Exception as err:
            records.append(failed_source(PROVIDER, "filings", str(err), symbol=symbol, exc=err))
    return pd.DataFrame(rows), records
