import unittest,datetime as dt
from refresh import parse,canonical
class CollectorTests(unittest.TestCase):
 def test_dates_and_markup(self):
  x=b'''<rss><channel><item><title>&lt;b&gt;CBD&lt;/b&gt;</title><link>https://example.org/a?utm_source=x</link><pubDate>Wed, 11 Nov 2026 08:00:00 GMT</pubDate><description>&lt;script&gt;foo&lt;/script&gt; hello</description></item><item><title>Old</title><link>https://example.org/b</link><pubDate>Mon, 09 Nov 2026 08:00:00 GMT</pubDate></item></channel></rss>'''
  items=parse(x,('Test','https://example.org/feed','fr','France'),dt.datetime(2026,11,11,9,tzinfo=dt.timezone.utc))
  self.assertEqual(len(items),1);self.assertEqual(items[0]['title'],'CBD');self.assertEqual(items[0]['url'],'https://example.org/a');self.assertNotIn('<',items[0]['excerpt'])
 def test_future_and_missing_date(self):
  self.assertEqual(parse(b'<rss><item><title>x</title><link>https://example.org</link></item></rss>',('T','x','fr','France'),dt.datetime.now(dt.timezone.utc)),[])
if __name__=='__main__':unittest.main()
