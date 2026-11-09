"""Tests hors ligne du collecteur quotidien (aucun appel HTTP)."""
import unittest
import refresh


class RefreshTests(unittest.TestCase):
    def test_google_rss_parse(self):
        feed = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0"><channel><title>News</title>
        <item><title>Test manufacturer announces new plant</title>
        <link>https://news.google.com/rss/articles/EXAMPLE</link>
        <pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate>
        <source url="https://example.org">Example Publisher</source></item>
        </channel></rss>"""
        items = refresh.parse_rss(feed, "Fabricants")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["topic"], "Fabricants")
        self.assertEqual(items[0]["domain"], "Example Publisher")
        self.assertEqual(items[0]["published_at"], "2026-11-09T10:00:00Z")

    def test_invalid_feed_is_error(self):
        with self.assertRaises(ValueError):
            refresh.parse_rss(b"<html><body>not a feed</body></html>", "Test")

    def test_bad_or_http_urls_rejected(self):
        self.assertEqual(refresh.https_url("http://example.com"), "")
        self.assertEqual(refresh.https_url("javascript:alert(1)"), "")
        self.assertEqual(refresh.https_url("https://example.org/path"), "https://example.org/path")

    def test_gdelt_date(self):
        self.assertEqual(refresh.gdelt_date("20261109T140000Z"), "2026-11-09T14:00:00Z")


if __name__ == "__main__":
    unittest.main()
