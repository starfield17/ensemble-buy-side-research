from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Market = Literal["US", "CN", "HK", "OTHER"]
AssetType = Literal["equity", "etf", "unknown"]


@dataclass(frozen=True)
class SecurityId:
    symbol: str
    market: Market
    asset_type: AssetType = "unknown"


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def infer_market(symbol: str) -> Market:
    value = normalize_symbol(symbol)
    if value.endswith((".SS", ".SZ", ".BJ")) or (value.isdigit() and len(value) == 6):
        return "CN"
    if value.endswith(".HK"):
        return "HK"
    if "." not in value or value.endswith(".US"):
        return "US"
    return "OTHER"


def bare_cn_symbol(symbol: str) -> str:
    return normalize_symbol(symbol).split(".")[0]


def tushare_symbol(symbol: str) -> str:
    value = normalize_symbol(symbol)
    if value.endswith((".SS", ".SZ", ".BJ")):
        code, suffix = value.rsplit(".", 1)
        return f"{code}.{'SH' if suffix == 'SS' else suffix}"
    if value.isdigit() and len(value) == 6:
        suffix = "SH" if value.startswith(("5", "6", "9")) else "SZ"
        return f"{value}.{suffix}"
    return value
