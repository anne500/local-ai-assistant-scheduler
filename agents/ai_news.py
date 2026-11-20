"""Summarize recent entries from one public AI publisher's RSS feed."""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from agents._ollama import summarize

NAME = "ai-news"
FEED_URL = "https://huggingface.co/blog/feed.xml"
MAX_ITEMS = 3


def feed_entries(xml_data: bytes) -> list[dict]:
    root = ET.fromstring(xml_data)
    entries = []
    seen = set()
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        parsed_url = urlparse(url)
        if not title or parsed_url.scheme != "https" or parsed_url.hostname != "huggingface.co":
            continue
        if url in seen:
            continue
        seen.add(url)
        description = unescape(item.findtext("description") or "")
        excerpt = " ".join(re.sub(r"<[^>]+>", " ", description).split())[:1800]
        published = (item.findtext("pubDate") or "").strip()
        try:
            published_time = parsedate_to_datetime(published)
            if published_time.tzinfo is None:
                published_time = published_time.replace(tzinfo=timezone.utc)
            published_utc = published_time.astimezone(timezone.utc).isoformat()
        except (ValueError, TypeError, OverflowError):
            published_utc = "Unavailable"
        entries.append({
            "title": title, "url": url,
            "published_utc": published_utc, "excerpt": excerpt,
        })
    entries.sort(
        key=lambda entry: entry["published_utc"] if entry["published_utc"] != "Unavailable" else "",
        reverse=True,
    )
    if not entries:
        raise ValueError("The RSS feed contained no usable Hugging Face entries.")
    return entries[:MAX_ITEMS]


def run() -> str:
    request = Request(FEED_URL, headers={"User-Agent": "local-ai-assistant-scheduler"})
    with urlopen(request, timeout=30) as response:
        entries = feed_entries(response.read())
    retrieved_at = datetime.now(timezone.utc).isoformat()
    sections = []
    for entry in entries:
        if entry["excerpt"]:
            entry["evidence_scope"] = "feed_excerpt"
            summary = summarize(
                "Write one short sentence summarizing the supplied RSS excerpt. "
                "Attribute claims to the post. Use only supplied facts. "
                "Do not add links, publication dates, authors, affiliations, "
                "rankings or claims of independent verification.",
                entry,
            )
        else:
            entry["evidence_scope"] = "headline_only"
            summary = "Headline only. The feed supplied no article excerpt."
        sections.append(
            f"## {entry['title']}\n\n{summary}\n\n"
            f"Published (UTC): {entry['published_utc']}\n\nSource: {entry['url']}\n"
        )
    return (
        "# AI News Digest: Hugging Face Blog\n\n"
        "Scope: up to three recent entries from one publisher's RSS feed. "
        "Each entry identifies whether a feed excerpt was available.\n\n"
        f"Feed: {FEED_URL}\n\nRetrieved at (UTC): {retrieved_at}\n\n"
        + "\n".join(sections)
        + f"\n## Source evidence\n\n```json\n{json.dumps(entries, indent=2)}\n```\n"
    )
