"""Offline checks for quote arithmetic, RSS boundaries, and report evidence."""

import json
import unittest
from unittest.mock import patch

from agents import ai_news, googl_stock, _ollama


def chart(price=100, previous=80):
    return {"chart": {"result": [{"meta": {
        "symbol": "GOOGL", "regularMarketPrice": price,
        "chartPreviousClose": previous, "currency": "USD",
        "regularMarketTime": 1700000000,
    }}], "error": None}}


RSS = b'''<rss><channel>
<item><title>Old</title><link>https://huggingface.co/blog/old</link><pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate></item>
<item><title>New</title><link>https://huggingface.co/blog/new</link><pubDate>Tue, 02 Jan 2024 10:00:00 GMT</pubDate><description>&lt;p&gt;New &amp;amp; useful&lt;/p&gt;</description></item>
<item><title>Duplicate</title><link>https://huggingface.co/blog/new</link></item>
<item><title>Other host</title><link>https://example.com/story</link></item>
<item><title>Unknown date</title><link>https://huggingface.co/blog/unknown</link><pubDate>invalid</pubDate></item>
</channel></rss>'''


class WorkerChecks(unittest.TestCase):
    def test_quote_increase(self):
        result = googl_stock.quote_evidence(chart())
        self.assertEqual((result["change"], result["percent_change"], result["direction"]), ("20.00", "25.00", "up"))

    def test_quote_decrease_and_unchanged(self):
        self.assertEqual(googl_stock.quote_evidence(chart(75, 100))["percent_change"], "-25.00")
        self.assertEqual(googl_stock.quote_evidence(chart(75, 100))["direction"], "down")
        self.assertEqual(googl_stock.quote_evidence(chart(100, 100))["direction"], "unchanged")

    def test_quote_invalid_values(self):
        for value in [0, -1, "NaN", "Infinity"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                googl_stock.quote_evidence(chart(previous=value))

    def test_quote_provider_error(self):
        with self.assertRaises(ValueError):
            googl_stock.quote_evidence({"chart": {"error": {"code": "Not Found"}, "result": None}})

    def test_quote_wrong_symbol(self):
        data = chart()
        data["chart"]["result"][0]["meta"]["symbol"] = "OTHER"
        with self.assertRaises(ValueError):
            googl_stock.quote_evidence(data)

    def test_rss_order_deduplication_and_host(self):
        entries = ai_news.feed_entries(RSS)
        self.assertEqual([e["title"] for e in entries], ["New", "Old", "Unknown date"])
        self.assertEqual(entries[0]["excerpt"], "New & useful")
        self.assertEqual(entries[-1]["published_utc"], "Unavailable")

    def test_empty_feed_fails(self):
        with self.assertRaises(ValueError):
            ai_news.feed_entries(b"<rss><channel/></rss>")

    @patch("agents.ai_news.urlopen")
    @patch("agents.ai_news.summarize", return_value="A summary.")
    def test_news_report_preserves_sources(self, summary, fetch):
        fetch.return_value.__enter__.return_value.read.return_value = RSS
        report = ai_news.run()
        self.assertEqual(summary.call_count, 1)
        self.assertIn("Source: https://huggingface.co/blog/new", report)
        self.assertIn("## Source evidence", report)
        self.assertIn("one publisher", report)


    @patch("agents.ai_news.urlopen")
    @patch("agents.ai_news.summarize")
    def test_headline_only_entries_skip_model(self, summary, fetch):
        fetch.return_value.__enter__.return_value.read.return_value = b"""<rss><channel>
        <item><title>A model efficiency claim</title>
        <link>https://huggingface.co/blog/example</link></item>
        </channel></rss>"""
        report = ai_news.run()
        summary.assert_not_called()
        self.assertIn("## A model efficiency claim", report)
        self.assertIn("Headline only. The feed supplied no article excerpt.", report)
        self.assertIn('"evidence_scope": "headline_only"', report)
        self.assertIn("Source: https://huggingface.co/blog/example", report)

    def test_observed_quote_arithmetic(self):
        result = googl_stock.quote_evidence(chart("272.66", "282.44"))
        self.assertEqual(result["change"], "-9.78")
        self.assertEqual(result["percent_change"], "-3.46")
        self.assertEqual(result["direction"], "down")

    @patch("agents.googl_stock.urlopen")
    @patch("agents.googl_stock.summarize", return_value="GOOGL retrieved quote.")
    def test_stock_report_retains_arithmetic(self, summary, fetch):
        fetch.return_value.__enter__.return_value.read.return_value = json.dumps(chart())
        report = googl_stock.run()
        self.assertIn('"percent_change": "25.00"', report)
        self.assertIn("Retrieved at (UTC)", report)

    @patch("agents._ollama.urlopen")
    def test_model_invalid_responses_fail(self, fetch):
        for content, done, reason in [("", True, "stop"), ("Partial", True, "length"), ("Partial", False, "stop")]:
            fetch.return_value.__enter__.return_value.read.return_value = json.dumps({
                "message": {"content": content}, "done": done, "done_reason": reason,
            })
            with self.subTest(content=content, done=done, reason=reason), self.assertRaises(RuntimeError):
                _ollama.summarize("Summarize", {})


if __name__ == "__main__":
    unittest.main()
