"""Revue de presse publique : RSS/Atom, archives quotidiennes, aucune API payante."""
from __future__ import annotations
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PARIS = ZoneInfo('Europe/Paris')
SOURCES = [
    ('Newsweed', 'https://www.newsweed.fr/feed/', 'fr', 'France'),
    ('Le Cannabiste', 'https://lecannabiste.com/feed/', 'fr', 'France'),
    ('Marijuana Moment', 'https://www.marijuanamoment.net/feed/', 'en', 'Monde'),
    ('Ganjapreneur', 'https://www.ganjapreneur.com/feed/', 'en', 'Monde'),
    ('Hanf Magazin', 'https://www.hanf-magazin.com/feed/', 'de', 'Europe'),
    ('Business of Cannabis', 'https://businessofcannabis.com/feed/', 'en', 'Europe'),
    ('HempToday', 'https://hemptoday.net/feed/', 'en', 'Monde'),
    ('Cannabis Health', 'https://cannabishealthnews.co.uk/feed/', 'en', 'Europe'),
    ('NORML', 'https://norml.org/feed/', 'en', 'Monde'),
]
UA = 'GardenzActuz/3.0 (revue de presse; extraits courts et liens vers les sources)'

def clean(value):
    value = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', value or '', flags=re.I | re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()

def canonical(value):
    try:
        parts = urllib.parse.urlsplit(value.strip())
        if parts.scheme != 'https' or not parts.hostname or parts.username:
            return ''
        query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query)
                 if not k.lower().startswith(('utm_', 'fbclid', 'gclid'))]
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, urllib.parse.urlencode(query), ''))
    except ValueError:
        return ''

def date(value):
    try:
        result = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, AttributeError):
        try:
            result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError, TypeError):
            return None
    return result.replace(tzinfo=dt.timezone.utc) if result.tzinfo is None else result

def classify(title, excerpt='', categories=''):
    text = (title + ' ' + excerpt + ' ' + categories).casefold()
    patterns = [
        ('Lois & société', r'loi|interdi|légal|legal|regulat|senat|congress|banking|government|vote|ban\b|policy|gesetz'),
        ('Santé & recherche', r'médic|medic|patient|study|studie|recherch|research|health|santé|clinical|wissenschaft'),
        ('CBD & molécules', r'\bcbd\b|cannabidiol|cannabino|\bhhc\b|\bthcp\b|\bthc\b'),
        ('Chanvre', r'chanvre|\bhemp\b|hanf|textil|fiber|fibre'),
        ('Économie', r'econom|économ|business|market|marché|entreprise|company|companies|invest|bank|sales|retail'),
        ('Culture', r'culture|snoop|music|musiqu|festival|artiste|club|cinéma|concert'),
    ]
    return [label for label, pattern in patterns if re.search(pattern, text)] or ['Autres actualités']

def short_excerpt(value, title):
    text = clean(value)
    if text.casefold().startswith(title.casefold()):
        text = text[len(title):].lstrip(' .:–—-')
    text = re.split(r'\b(?:The post|Cet article|La version originale de ce contenu|L’article .* est apparu)\b', text)[0].strip()
    if len(text) > 220:
        text = text[:220].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'
    return text

def parse(blob, source, now, window_hours=24):
    name, feed_url, lang, region = source
    root = ET.fromstring(blob)
    atom = '{http://www.w3.org/2005/Atom}'
    entries = root.findall('.//item') + root.findall(f'{atom}entry')
    if root.tag.split('}')[-1] not in ('rss', 'RDF', 'feed'):
        raise ValueError('Le document reçu n’est pas un flux RSS/Atom')
    out = {}
    for item in entries:
        title = clean(item.findtext('title') or item.findtext(f'{atom}title'))
        link = item.findtext('link')
        if not link:
            link = next((n.get('href') for n in item.findall(f'{atom}link') if n.get('rel', 'alternate') == 'alternate'), '')
        link = canonical(link or '')
        published = date(item.findtext('pubDate') or item.findtext(f'{atom}published') or item.findtext('{http://purl.org/dc/elements/1.1/}date'))
        if not title or not link or not published:
            continue
        if not now - dt.timedelta(hours=window_hours) <= published <= now:
            continue
        excerpt = short_excerpt(item.findtext('description') or item.findtext(f'{atom}summary') or '', title)
        categories = ' '.join(clean(n.text or n.get('term', '')) for n in item if n.tag.split('}')[-1] == 'category')
        kind = 'Opinion' if re.search(r'op-ed|opinion|tribune|commentary', title + ' ' + categories, re.I) else 'Article'
        if re.search(r'press release|communiqué', title + ' ' + categories, re.I):
            kind = 'Communiqué'
        image_url = ''
        for n in item.iter():
            if n.tag.endswith(('thumbnail', 'content', 'enclosure')):
                candidate = n.get('url', '')
                if candidate and (n.get('type', '').startswith('image/') or 'thumbnail' in n.tag or 'medium' in n.attrib):
                    image_url = canonical(candidate)
                    break
        ident = hashlib.sha256(link.encode()).hexdigest()[:20]
        out[ident] = dict(id=ident, title=title, url=link, source=name, sourceFeed=feed_url,
                          language=lang, region=region, publishedAt=published.isoformat(), collectedAt=now.isoformat(),
                          excerpt=excerpt, topics=classify(title, excerpt, categories), kind=kind, image='', credit='', feedImage=image_url)
    return sorted(out.values(), key=lambda value: value['publishedAt'], reverse=True)

def fetch(source, now, window_hours=24):
    name, url, *_ = source
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/rss+xml,application/atom+xml,application/xml,text/xml'})
        with urllib.request.urlopen(req, timeout=22) as response:
            blob = response.read(3_000_001)
            if len(blob) > 3_000_000:
                raise ValueError('Flux trop volumineux')
        items = parse(blob, source, now, window_hours)
        return items, dict(name=name, url=url, ok=True, count=len(items), checkedAt=now.isoformat())
    except Exception as error:
        reason = 'HTTP ' + str(error.code) if hasattr(error, 'code') else type(error).__name__
        return [], dict(name=name, url=url, ok=False, count=0, checkedAt=now.isoformat(), error=reason)

class MetaImage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = ''
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('property', attrs.get('name', '')).lower() == 'og:image':
            self.url = attrs.get('content', '')

def image(item):
    """Actual source imagery only; a refusal leaves the story text-only."""
    try:
        image_url = item.pop('feedImage', '')
        if not image_url:
            req = urllib.request.Request(item['url'], headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=12) as response:
                parser = MetaImage()
                parser.feed(response.read(1_500_000).decode('utf-8', 'replace'))
            image_url = canonical(urllib.parse.urljoin(item['url'], parser.url)) if parser.url else ''
        if not image_url:
            return
        with urllib.request.urlopen(urllib.request.Request(image_url, headers={'User-Agent': UA}), timeout=12) as response:
            content_type = response.headers.get_content_type()
            blob = response.read(1_500_001)
        extension = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}.get(content_type)
        if not extension or len(blob) > 1_500_000:
            return
        relative = 'assets/live-' + hashlib.sha256(blob).hexdigest()[:20] + '.' + extension
        (ROOT / relative).write_bytes(blob)
        item.update(image=relative, imageSource=image_url, credit=item['source'] + ' · image de l’article')
    except Exception:
        pass

def read_json(path, fallback):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return fallback

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)

def publish(results, now, previous):
    fresh = {item['id']: item for items, _ in results for item in items}
    health = [state for _, state in results]
    ok = sum(source['ok'] for source in health)
    stored = {item['id']: item for item in previous.get('items', [])
              if date(item.get('publishedAt')) and date(item['publishedAt']) >= now - dt.timedelta(days=30)}
    for ident, item in fresh.items():
        if ident in stored:
            item.update({key: value for key, value in stored[ident].items() if key in ('image', 'imageSource', 'credit', 'collectedAt', 'translation')})
        stored[ident] = item
    for item in stored.values():
        item['excerpt'] = short_excerpt(item.get('excerpt', ''), item['title'])
        item.setdefault('topics', classify(item['title'], item.get('excerpt', '')))
        item.setdefault('kind', 'Article')
    candidates = sorted((item for item in fresh.values() if not item.get('image')),
                        key=lambda item: (item['language'] != 'fr', -date(item['publishedAt']).timestamp()))[:18]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(image, candidates))
    for item in stored.values():
        item.pop('feedImage', None)
    data = dict(version=3, mode='public-rss', attemptedAt=now.isoformat(),
                lastSuccess=now.isoformat() if ok else previous.get('lastSuccess'),
                status='ok' if ok == len(SOURCES) else 'partial' if ok else 'error', sources=health,
                items=sorted(stored.values(), key=lambda item: date(item['publishedAt']), reverse=True), windowHours=24,
                schedule='09h17, 13h17 et 18h17 · Paris',
                notice='Revue de presse automatique. Titres et courts extraits dans la langue des sources ; articles à lire chez leurs éditeurs. Les rubriques sont un classement automatique, pas une validation des informations.')
    write_json(ROOT / 'data/latest.json', data)
    history = ROOT / 'data/history'
    history.mkdir(exist_ok=True)
    if ok:
        day = now.astimezone(PARIS).date().isoformat()
        snapshot_path = history / (day + '.json')
        old_day = read_json(snapshot_path, {})
        daily = {item['id']: item for item in old_day.get('items', [])}
        for item in daily.values():
            item['excerpt'] = short_excerpt(item.get('excerpt', ''), item['title'])
        daily.update({item['id']: item for item in stored.values() if date(item['publishedAt']) >= now - dt.timedelta(hours=24)})
        snapshot = {**data, 'date': day, 'items': sorted(daily.values(), key=lambda item: date(item['publishedAt']), reverse=True)}
        write_json(snapshot_path, snapshot)
    editions = []
    for path in sorted(history.glob('????-??-??.json'), reverse=True):
        snapshot = read_json(path, {})
        if snapshot.get('lastSuccess'):
            editions.append(dict(date=path.stem, path='data/history/' + path.name,
                                 count=len(snapshot.get('items', [])), lastSuccess=snapshot['lastSuccess']))
    write_json(ROOT / 'data/index.json', {'version': 1, 'editions': editions})
    return data, len(fresh), ok

def main():
    now = dt.datetime.now(dt.timezone.utc)
    previous = read_json(ROOT / 'data/latest.json', {})
    last = date(previous.get('lastSuccess'))
    if '--if-needed' in sys.argv and last and (now - last).total_seconds() < 4 * 3600:
        print('Collecte récente conservée.')
        return
    window = min(14 * 24, max(48, int((now - last).total_seconds() / 3600) + 24)) if last else 7 * 24
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda source: fetch(source, now, window), SOURCES))
    data, fresh_count, ok = publish(results, now, previous)
    print(f'{ok}/{len(SOURCES)} sources accessibles · {fresh_count} publications collectées · {len(data["items"])} conservées')
    if not ok:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
