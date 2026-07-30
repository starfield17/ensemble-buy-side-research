from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    sec_user_agent: str | None
    tushare_token: str | None
    request_timeout: int
    cache_dir: Path


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv()
    return Settings(
        sec_user_agent=os.getenv("SEC_USER_AGENT"),
        tushare_token=os.getenv("TUSHARE_TOKEN"),
        request_timeout=int(os.getenv("ENSEMBLE_RESEARCH_REQUEST_TIMEOUT", os.getenv("BUY_SIDE_REQUEST_TIMEOUT", "20"))),
        cache_dir=Path(os.getenv("ENSEMBLE_RESEARCH_CACHE_DIR", ".cache/ensemble-research")),
    )


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]
