import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('actuz_refresh', Path(__file__).with_name('refresh.py'))
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)
NOW = dt.datetime(2026, 11, 11, 9, tzinfo=dt.timezone.utc)
SOURCE = ('Test', 'https://example.org/feed', 'fr', 'France')

def rss(items):
    return ('<rss><channel>' + ''.join('<item><title>' + title + '</title><link>' + link + '</link><pubDate>' + published + '</pubDate><description>' + description + '</description></item>' for title, link, published, description in items) + '</channel></rss>').encode()

class CollectorTests(unittest.TestCase):
    def test_markup_dates_tracking_and_duplicate(self):
        data = rss([('&lt;b&gt;CBD&lt;/b&gt;', 'https://example.org/a?utm_source=x', 'Wed, 11 Nov 2026 08:00:00 GMT', '&lt;script&gt;bad()&lt;/script&gt; bonjour'), ('CBD', 'https://example.org/a', 'Wed, 11 Nov 2026 08:00:00 GMT', 'bonjour'), ('Old', 'https://example.org/b', 'Mon, 09 Nov 2026 08:00:00 GMT', '')])
        items = refresh.parse(data, SOURCE, NOW)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['url'], 'https://example.org/a')
        self.assertNotIn('bad()', items[0]['excerpt'])
        self.assertEqual(items[0]['title'], 'CBD')

    def test_no_arbitrary_four_article_limit(self):
        data = rss([(f'Article {n}', f'https://example.org/{n}', 'Wed, 11 Nov 2026 08:00:00 GMT', '') for n in range(12)])
        self.assertEqual(len(refresh.parse(data, SOURCE, NOW)), 12)

    def test_future_unsafe_and_missing_dates_are_rejected(self):
        data = rss([('Future', 'https://example.org/future', 'Thu, 12 Nov 2026 08:00:00 GMT', ''), ('Invalid', 'javascript:alert(1)', 'Wed, 11 Nov 2026 08:00:00 GMT', ''), ('No date', 'https://example.org/no-date', '', '')])
        self.assertEqual(refresh.parse(data, SOURCE, NOW), [])
        with self.assertRaises(ValueError):
            refresh.parse(b'<html><body>Error</body></html>', SOURCE, NOW)

    def test_atom_publication_not_modified_date(self):
        data = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Medical research</title><link href="https://example.org/a"/><published>2026-11-11T08:00:00Z</published></entry><entry><title>Updated old article</title><link href="https://example.org/old"/><updated>2026-11-11T08:00:00Z</updated></entry></feed>'
        self.assertEqual(len(refresh.parse(data, SOURCE, NOW)), 1)

    def test_failure_preserves_last_success_and_never_creates_fake_daily_edition(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(refresh, 'ROOT', Path(directory)), patch.object(refresh, 'image'):
            item = refresh.parse(rss([('CBD', 'https://example.org/a', 'Wed, 11 Nov 2026 08:00:00 GMT', '')]), SOURCE, NOW)[0]
            good = [([item], dict(name='Test', url=SOURCE[1], ok=True))]
            first, _, _ = refresh.publish(good, NOW, {})
            failed = [([], dict(name='Test', url=SOURCE[1], ok=False))]
            tomorrow = NOW + dt.timedelta(days=1)
            second, _, _ = refresh.publish(failed, tomorrow, first)
            self.assertEqual(second['lastSuccess'], first['lastSuccess'])
            self.assertEqual(second['status'], 'error')
            self.assertEqual(len(second['items']), 1)
            self.assertFalse((Path(directory) / 'data/history/2026-11-12.json').exists())
            index = json.loads((Path(directory) / 'data/index.json').read_text())
            self.assertEqual([e['date'] for e in index['editions']], ['2026-11-11'])

    def test_same_day_collects_cumulative_unique_articles(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(refresh, 'ROOT', Path(directory)), patch.object(refresh, 'image'):
            first_item = refresh.parse(rss([('One', 'https://example.org/one', 'Wed, 11 Nov 2026 08:00:00 GMT', '')]), SOURCE, NOW)[0]
            health = dict(name='Test', url=SOURCE[1], ok=True)
            first, _, _ = refresh.publish([([first_item], health)], NOW, {})
            later = NOW + dt.timedelta(hours=6)
            new_item = refresh.parse(rss([('Two', 'https://example.org/two', 'Wed, 11 Nov 2026 14:00:00 GMT', '')]), SOURCE, later)[0]
            refresh.publish([([new_item, first_item], health)], later, first)
            snapshot = json.loads((Path(directory) / 'data/history/2026-11-11.json').read_text())
            self.assertEqual(len(snapshot['items']), 2)
            self.assertEqual(len({i['id'] for i in snapshot['items']}), 2)

if __name__ == '__main__':
    unittest.main()
