"""Summarize a retrieved GOOGL quote with Python-computed changes."""

import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from urllib.request import Request, urlopen

from agents._ollama import summarize

NAME = "googl-stock"
SOURCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/GOOGL?interval=1d&range=1d"


def quote_evidence(data: dict) -> dict:
    chart = data["chart"]
    if chart.get("error") or not chart.get("result"):
        raise ValueError("Yahoo returned no usable chart result.")
    meta = chart["result"][0]["meta"]
    price = Decimal(str(meta["regularMarketPrice"]))
    previous = Decimal(str(meta["chartPreviousClose"]))
    if not price.is_finite() or not previous.is_finite() or price <= 0 or previous <= 0:
        raise ValueError("Quote prices must be finite positive numbers.")
    if meta.get("symbol") != "GOOGL":
        raise ValueError("The response symbol does not match GOOGL.")
    change = price - previous
    percent = change / previous * 100
    timestamp = meta.get("regularMarketTime")
    quote_time = (
        datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
        if timestamp is not None else "Unavailable"
    )
    return {
        "symbol": "GOOGL",
        "currency": meta.get("currency", "Unavailable"),
        "price": str(price), "previous_close": str(previous),
        "change": str(change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "percent_change": str(percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "direction": "up" if change > 0 else "down" if change < 0 else "unchanged",
        "quote_time_utc": quote_time,
        "market_state": meta.get("marketState", "Unavailable"),
    }


def run() -> str:
    request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    evidence = quote_evidence(data)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    summary = summarize(
        "Write one short sentence reporting the supplied symbol, quote price, "
        "currency, percentage change and direction relative to previous_close. "
        "Use only the supplied values. Describe it as the retrieved quote. "
        "Do not claim it is today's closing price. Do not infer causes or give advice.",
        evidence,
    )
    return (
        "# GOOGL Quote Brief\n\n"
        f"{summary}\n\n## Source evidence\n\n"
        f"Source: {SOURCE_URL}\n\nRetrieved at (UTC): {retrieved_at}\n\n"
        "Changes are computed in Python against chartPreviousClose.\n\n"
        f"```json\n{json.dumps(evidence, indent=2)}\n```\n"
    )
