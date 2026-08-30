import unittest
from datetime import datetime, timezone

from source_pilot import record, run

RSS = """<rss><channel><item><title>Useful prototype</title><link>https://example.com/one</link><pubDate>Sat, 29 Aug 2026 12:00:00 GMT</pubDate><description>Hands-on report</description></item></channel></rss>"""
ATOM = """<feed xmlns="http://www.w3.org/2005/Atom"><entry xml:lang="en"><title>New project</title><link href="https://example.com/project"/><updated>2026-08-29T12:00:00Z</updated><summary>Prototype</summary></entry></feed>"""


class SourcePilotTests(unittest.TestCase):
    def test_success_and_failure_are_both_recorded(self):
        config = {"sources": [{"source": "Good", "url": "good", "page": "Ideas"}, {"source": "Bad", "url": "bad", "page": "Ideas"}]}
        def fetcher(url):
            if url == "bad":
                raise TimeoutError("timed out")
            return RSS
        state = run(config, now=datetime(2026, 8, 29, 13, tzinfo=timezone.utc), fetcher=fetcher)
        self.assertEqual(1, state["summary"]["Good"]["items_observed"])
        self.assertEqual(0, state["summary"]["Bad"]["successful_runs"])

    def test_verdict_waits_for_full_observation_window(self):
        row = {"source": "Good", "page": "Ideas", "ok": True, "items": 2, "unique_urls": 2, "promotional": 0}
        first = record({}, [row], "2026-08-29T00:00:00+00:00", 48)
        second = record(first, [row], "2026-08-31T00:00:00+00:00", 48)
        self.assertFalse(first["summary"]["Good"]["eligible_for_verdict"])
        self.assertTrue(second["summary"]["Good"]["eligible_for_verdict"])

    def test_atom_entry_attributes_are_supported(self):
        config = {"sources": [{"source": "Atom", "url": "atom", "page": "Ideas"}]}
        state = run(config, now=datetime(2026, 8, 29, 13, tzinfo=timezone.utc),
                    fetcher=lambda _: ATOM)
        self.assertEqual(1, state["summary"]["Atom"]["items_observed"])


if __name__ == "__main__":
    unittest.main()
