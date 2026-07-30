from __future__ import annotations

import hashlib
import re
from datetime import date
from urllib.parse import quote_plus

import pandas as pd
import requests

from ...models import SourceRecord
from .common import failed_source

PROVIDER = "gdelt"


def _id(title: str, url: str | None) -> str:
    return hashlib.sha1(f"{title}|{url or ''}".encode()).hexdigest()[:16]


def fetch_news(query: str, start: str | None = None, end: str | None = None, timeout: int = 20, max_records: int = 100) -> tuple[pd.DataFrame, list[SourceRecord]]:
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": str(max_records),
        "format": "json",
        "sort": "HybridRel",
    }
    if start:
        params["startdatetime"] = re.sub(r"\D", "", start)[:8] + "000000"
    if end:
        params["enddatetime"] = re.sub(r"\D", "", end)[:8] + "235959"
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + "&".join(f"{key}={quote_plus(value)}" for key, value in params.items())
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "ensemble-buy-side-research/0.3"})
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return pd.DataFrame(), [failed_source(PROVIDER, "news", str(exc), exc=exc)]
    rows = []
    for article in payload.get("articles", []):
        title = article.get("title") or "Untitled"
        article_url = article.get("url")
        rows.append(
            {
                "id": _id(title, article_url),
                "query": query,
                "title": title,
                "url": article_url,
                "publisher": article.get("domain"),
                "published_at": article.get("seendate"),
                "language": article.get("language"),
                "source_country": article.get("sourcecountry"),
                "provider": PROVIDER,
                "retrieved_on": date.today().isoformat(),
            }
        )
    return pd.DataFrame(rows), [SourceRecord(provider=PROVIDER, dataset="news", status="success" if rows else "partial", record_count=len(rows), notes=[] if rows else ["No matching articles returned."])]
