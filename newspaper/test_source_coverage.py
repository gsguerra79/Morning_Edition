import unittest

from source_coverage import build, runtime_scope


class SourceCoverageTests(unittest.TestCase):
    def test_full_scope_exposes_loaded_and_connector_sources(self):
        registry = {"generated_at": "2026-08-30T00:00:00Z", "sources": [
            {"source": "Active", "topics": ["World News"], "what_i_read": "News",
             "must_include": "Major events", "avoid": "Filler",
             "adapters": [{"type": "rss", "status": "active", "url": "https://a.test/feed/"}]},
            {"source": "Planned", "topics": ["Ideas"],
             "adapters": [{"type": "connector", "status": "planned"}]},
        ]}
        result = build(registry, [{"url": "https://a.test/feed"}],
                       {"articles": [{"source": "Active"}],
                        "feed_health": [{"url": "https://a.test/feed", "status": "fetched", "items": 1}]},
                       {"sources": {"Active": {}}})
        self.assertEqual(2, result["summary"]["sources"])
        self.assertEqual(2, result["summary"]["pages"])
        self.assertEqual(1, result["summary"]["fully_loaded"])
        rows = {row["source"]: row for page in result["pages"] for row in page["sources"]}
        self.assertEqual("loaded", rows["Active"]["ingestion_state"])
        self.assertEqual("healthy", rows["Active"]["health_state"])
        self.assertEqual("connector-needed", rows["Planned"]["adapter_state"])

    def test_missing_assets_are_visible_warnings(self):
        result = build({}, [], {}, None)
        self.assertEqual("missing", result["registry"]["status"])
        self.assertEqual("missing", result["rules"]["status"])
        self.assertEqual(2, len(result["warnings"]))

    def test_runtime_scope_uses_all_active_rss_adapters_and_owner_pages(self):
        registry = {"sources": [
            {"source": "Multi", "topics": ["Technology & Things", "Ideas"],
             "adapters": [
                 {"type": "rss", "status": "active", "url": "https://multi.test/feed"},
                 {"type": "connector", "status": "planned"},
             ]},
            {"source": "Gap", "topics": ["World News"],
             "adapters": [{"type": "connector", "status": "planned"}]},
        ]}
        categories, feeds = runtime_scope(registry)
        self.assertEqual(7, len(categories))
        self.assertEqual([{"url": "https://multi.test/feed", "source": "Multi",
                           "category": "technology"}], feeds)

    def test_reader_added_feed_appears_in_inventory(self):
        result = build(
            {"generated_at": "2026-08-30T00:00:00Z", "sources": []},
            [{"url": "https://new.test/feed", "source": "New Source",
              "category": "technology"}],
            {"feed_health": [{"url": "https://new.test/feed", "status": "fetched",
                              "items": 3}]},
            {"sources": {}},
        )
        rows = [row for page in result["pages"] for row in page["sources"]]
        self.assertEqual("New Source", rows[0]["source"])
        self.assertEqual("reader", rows[0]["origin"])
        self.assertEqual("healthy", rows[0]["health_state"])

    def test_runtime_alias_is_merged_into_detailed_canonical_source(self):
        result = build(
            {"generated_at": "2026-08-30T00:00:00Z", "sources": [{
                "source": "Financial Times", "topics": ["World News"],
                "what_i_read": "World and US news", "must_include": "Major events",
                "adapters": [{"type": "connector", "status": "planned"}],
            }]},
            [
                {"url": "https://ft.test/us", "source": "Financial Times US",
                 "category": "worldnews"},
                {"url": "https://ft.test/world", "source": "Financial Times World",
                 "category": "worldnews"},
            ],
            {"articles": [{"source": "Financial Times US"}], "feed_health": [
                {"url": "https://ft.test/us", "status": "fetched", "items": 1},
                {"url": "https://ft.test/world", "status": "fetched", "items": 2},
            ]},
            {"sources": {}},
        )
        rows = [row for page in result["pages"] for row in page["sources"]]
        self.assertEqual(1, len(rows))
        self.assertEqual("Financial Times", rows[0]["source"])
        self.assertEqual("World and US news", rows[0]["what_i_read"])
        self.assertEqual("Major events", rows[0]["must_include"])
        self.assertEqual("active", rows[0]["adapter_state"])
        self.assertEqual("loaded", rows[0]["ingestion_state"])
        self.assertEqual(2, rows[0]["active_adapters"])
        self.assertEqual(1, rows[0]["current_items"])
        self.assertEqual(1, result["summary"]["sources"])
        self.assertEqual(0, result["summary"]["connector_gaps"])

    def test_multi_topic_source_appears_as_one_inventory_card(self):
        result = build(
            {"sources": [{
                "source": "BBC", "topics": ["World News"],
                "adapters": [{"type": "rss", "status": "active",
                              "url": "https://bbc.test/world"}],
            }]},
            [
                {"url": "https://bbc.test/world", "source": "BBC",
                 "category": "worldnews"},
                {"url": "https://bbc.test/football", "source": "BBC Football",
                 "category": "sports"},
            ],
            {"feed_health": [
                {"url": "https://bbc.test/world", "status": "fetched", "items": 1},
                {"url": "https://bbc.test/football", "status": "fetched", "items": 1},
            ]},
            {"sources": {}},
        )
        rows = [row for page in result["pages"] for row in page["sources"]]
        self.assertEqual(1, len(rows))
        self.assertEqual(["World News", "Sports"], rows[0]["topics"])
        self.assertEqual(2, rows[0]["active_adapters"])


if __name__ == "__main__":
    unittest.main()
