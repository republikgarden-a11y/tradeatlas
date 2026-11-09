#!/usr/bin/env python3
"""TRADE ATLAS · veille gratuite et quotidienne (mentions presse, pas BOL).

Sources : API publique GDELT DOC 2.0, ArtList / JSON. Aucune requête automatique
sur ImportYeti ou Volza. Bibliothèque standard uniquement, aucune clé.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "veille.json"
API = "https://api.gdeltproject.org/api/v2/doc/doc"
TOPICS = [
    ("Papiers et cônes", '("rolling paper" OR "pre rolled cones" OR "cigarette papers")'),
    ("Vaporisateurs et accessoires", '("vaporizer manufacturer" OR "vape manufacturer" OR "smoking accessories")'),
    ("Packaging et chanvre", '("cannabis packaging" OR "hemp packaging" OR "CBD manufacturing")'),
    ("Fabricants suivis · papier", '("Mitra Prodin" OR "Randi Cones" OR "Republic Technologies")'),
    ("Fabricants suivis · vapoteuses", '("Smoore" OR "Ispire Technology" OR "Storz & Bickel")'),
    ("Fabricants suivis · emballage", '("Berlin Packaging" OR "Dymapak" OR "Boveda")'),
    ("Marques et distributeurs", '("Futurola" OR "HBI International" OR "Blazy Susan")'),
]


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_seen(value: str) -> str:
    v = (value or "").strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return dt.datetime.strptime(v, fmt).replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            continue
    return ""


def as_https(url: str) -> str:
    try:
        p = urlparse(url)
    except ValueError:
        return ""
    return url if p.scheme == "https" and p.hostname else ""


def get_articles(topic: str, query: str) -> list[dict]:
    params = {"query": query, "mode": "artlist", "format": "json", "timespan": "7d", "maxrecords": 20, "sort": "datedesc"}
    url = API + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; TradeAtlasNewsMonitor/1.0)", "Accept": "application/json"})
    with urlopen(req, timeout=18) as r:
        if r.status != 200:
            raise ValueError(f"GDELT HTTP {r.status}")
        body = r.read(2_000_000)
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("articles", []), list):
        raise ValueError("Format GDELT inattendu")
    result=[]
    for x in payload.get("articles", []):
        if not isinstance(x,dict): continue
        valid=as_https(x.get("url", "")); title=re.sub(r"\s+", " ", str(x.get("title", "")).strip())[:260]
        if not valid or len(title)<8: continue
        result.append({"url":valid,"title":title,"topic":topic,
                       "domain":str(x.get("domain", ""))[:100],
                       "published_at":parse_seen(str(x.get("seendate", "")))})
    return result


def main() -> int:
    try:
        old=json.loads(DEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        old={"articles": []}
    checked=iso_now()
    old_articles={a.get("url"):a for a in old.get("articles", []) if isinstance(a,dict) and as_https(a.get("url", ""))}
    articles=dict(old_articles)
    errors=[]; successes=0; new=0
    for i,(topic,query) in enumerate(TOPICS):
        try:
            records=get_articles(topic,query)
            for a in records:
                if a["url"] not in articles:
                    a["first_seen"]=checked;articles[a["url"]]=a;new+=1
                else:
                    previous=articles[a["url"]]
                    a["first_seen"]=previous.get("first_seen",checked)
                    articles[a["url"]]={**previous,**a}
            successes+=1
            print(f"{topic}: {len(records)} mentions",flush=True)
        except Exception as e:
            errors.append(f"{topic}: {type(e).__name__} {str(e)[:150]}")
            print("Source momentanément indisponible:",errors[-1],file=sys.stderr,flush=True)
        if i<len(TOPICS)-1: time.sleep(2)
    cutoff=dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=90)
    def keep(a):
        date=a.get("published_at", "")
        try:return dt.datetime.fromisoformat(date.replace("Z","+00:00"))>=cutoff
        except (ValueError,TypeError):return False
    ordered=sorted((a for a in articles.values() if keep(a)),key=lambda a:(a.get("published_at", ""),a.get("first_seen", "")),reverse=True)[:120]
    outcome = "ok" if successes==len(TOPICS) else "partial" if successes else "error"
    payload={"schema":1,"status":outcome,"checked_at":checked,
             "last_success":checked if successes else old.get("last_success"),
             "topics_checked":len(TOPICS),"successful_topics":successes,
             "new_items":new,"errors":errors,"articles":ordered}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Veille {outcome}: {successes}/{len(TOPICS)} sources, {len(ordered)} liens archivés, {new} nouveaux.")
    return 0 if successes else 1

if __name__ == "__main__":
    sys.exit(main())
