#!/usr/bin/env python3
"""TRADE ATLAS - veille quotidienne gratuite (actualités, jamais données douanières).

Interroge un petit nombre de flux Google News RSS publics. Si tous les flux
échouent, essaie UNE requête GDELT DOC API. Pas d'API payante, pas de scraping
ImportYeti / Volza. Les résultats sont des pistes à vérifier, pas des preuves.
"""
from __future__ import annotations

import datetime as dt
from email.utils import parsedate_to_datetime
from http.client import HTTPException
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "veille.json"
RSS_URL = "https://news.google.com/rss/search"
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TradeAtlasDailyWatcher/1.1)",
           "Accept": "application/rss+xml, application/xml, application/json;q=0.8"}
# Quatre recherches groupées par jour ; 5,5 s entre elles pour éviter les rafales.
RSS_SEARCHES = [
    ("Papier & cônes", '"rolling papers" manufacturer OR "pre rolled cones" manufacturer when:7d'),
    ("Vape & accessoires", '"vaporizer manufacturer" OR "vape manufacturer" OR "smoking accessories" when:7d'),
    ("Packaging & chanvre", '"cannabis packaging" OR "hemp packaging" OR "CBD manufacturer" when:7d'),
    ("Fabricants & marques suivis", '"Mitra Prodin" OR "Republic Technologies" OR "Futurola" OR "Smoore" OR "Boveda" when:7d'),
]


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def date_utc(value: str) -> str:
    if not value:
        return ""
    try:
        d = parsedate_to_datetime(value)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError, IndexError, OverflowError):
        return ""


def gdelt_date(value: str) -> str:
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
        try:
            return dt.datetime.strptime(value, fmt).replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            pass
    return ""


def https_url(value: str) -> str:
    if not isinstance(value, str):
        return ""
    try:
        p = urlparse(value.strip())
        return value.strip() if p.scheme == "https" and p.hostname else ""
    except ValueError:
        return ""


def fetch_bytes(url: str, accept: str = "application/rss+xml", timeout: int = 20) -> bytes:
    headers = {**HEADERS, "Accept": accept}
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        return response.read(2_500_000)


def parse_rss(data: bytes, topic: str) -> list[dict]:
    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Réponse reçue mais flux RSS absent")
    rows = []
    for item in channel.findall("item")[:35]:
        title = re.sub(r"\s+", " ", (item.findtext("title") or "").strip())[:260]
        url = https_url(item.findtext("link") or "")
        pub = date_utc(item.findtext("pubDate") or "")
        source = item.find("source")
        source_name = source.text.strip() if source is not None and source.text else "Google News"
        if len(title) < 8 or not url or not pub:
            continue
        rows.append({"url": url, "title": title, "topic": topic,
                     "domain": source_name[:100], "published_at": pub})
    return rows


def google_news(topic: str, query: str) -> list[dict]:
    params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    return parse_rss(fetch_bytes(RSS_URL + "?" + urlencode(params)), topic)


def gdelt_fallback() -> list[dict]:
    # Un seul appel par jour, et uniquement si tous les flux RSS ont échoué.
    params = {"query": '("rolling papers" OR "cannabis packaging" OR "vape manufacturer")',
              "mode": "artlist", "format": "json", "timespan": "7d",
              "maxrecords": 30, "sort": "datedesc"}
    payload = json.loads(fetch_bytes(GDELT_URL + "?" + urlencode(params),
                                     accept="application/json", timeout=20))
    if not isinstance(payload, dict) or not isinstance(payload.get("articles"), list):
        raise ValueError("Réponse GDELT inattendue")
    rows = []
    for item in payload["articles"]:
        if not isinstance(item, dict):
            continue
        url = https_url(item.get("url", ""))
        title = re.sub(r"\s+", " ", str(item.get("title", "")))[:260].strip()
        date = gdelt_date(str(item.get("seendate", "")))
        if url and date and len(title) >= 8:
            rows.append({"url": url, "title": title, "topic": "Veille internationale",
                         "domain": str(item.get("domain", "GDELT"))[:100],
                         "published_at": date})
    return rows


def main() -> int:
    try:
        old = json.loads(DEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        old = {"articles": []}
    checked = iso_now()
    articles = {a["url"]: a for a in old.get("articles", [])
                if isinstance(a, dict) and https_url(a.get("url", ""))}
    errors: list[str] = []
    successes = 0
    new = 0

    def add_rows(rows: list[dict]) -> None:
        nonlocal new
        for item in rows:
            url = item["url"]
            if url in articles:
                previous = articles[url]
                articles[url] = {**previous, **item, "first_seen": previous.get("first_seen", checked)}
            else:
                item["first_seen"] = checked
                articles[url] = item
                new += 1

    for idx, (topic, query) in enumerate(RSS_SEARCHES):
        try:
            rows = google_news(topic, query)
            add_rows(rows)
            successes += 1
            print(f"{topic}: flux RSS OK / {len(rows)} résultats", flush=True)
        except (HTTPError, URLError, TimeoutError, ET.ParseError, ValueError, HTTPException) as exc:
            code = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
            errors.append(f"Google News · {topic}: {code} {str(exc)[:110]}")
            print(errors[-1], file=sys.stderr, flush=True)
        if idx < len(RSS_SEARCHES)-1:
            time.sleep(5.5)

    attempts = len(RSS_SEARCHES)
    if successes == 0:
        # Source de secours : respecter une seule requête GDELT (pas de boucle 429).
        time.sleep(6)
        attempts += 1
        try:
            rows = gdelt_fallback()
            add_rows(rows)
            successes += 1
            print(f"GDELT : secours OK / {len(rows)} résultats", flush=True)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError, HTTPException) as exc:
            errors.append(f"GDELT secours: {type(exc).__name__} {str(exc)[:110]}")
            print(errors[-1], file=sys.stderr, flush=True)

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)
    def keep(a: dict) -> bool:
        try:
            date = dt.datetime.fromisoformat(a.get("published_at", "").replace("Z", "+00:00"))
            return date >= cutoff
        except (ValueError, TypeError):
            return False
    history = sorted((a for a in articles.values() if keep(a)),
                     key=lambda a: (a.get("published_at", ""), a.get("first_seen", "")),
                     reverse=True)[:120]
    outcome = "ok" if successes == attempts else "partial" if successes else "error"
    result = {"schema": 1, "status": outcome, "checked_at": checked,
              "last_success": checked if successes else old.get("last_success"),
              "topics_checked": attempts, "successful_topics": successes,
              "new_items": new, "errors": errors, "articles": history}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"TRADE ATLAS: {outcome}, {successes}/{attempts} flux OK, {len(history)} articles, {new} nouveaux.")
    return 0 if successes else 1


if __name__ == "__main__":
    sys.exit(main())
