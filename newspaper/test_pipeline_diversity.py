import unittest
from datetime import datetime, timedelta, timezone

import pipeline


class PipelineDiversityTests(unittest.TestCase):
    def test_balanced_issue_protects_every_page_and_sports_subtopic(self):
        now = datetime.now(timezone.utc).isoformat()
        items = []
        for page, (minimum, _) in pipeline.PAGE_BUDGETS.items():
            if page == "sports":
                continue
            for i in range(minimum + 3):
                source = (("GiantITP", "Wilde Life")[i % 2]
                          if page == "comics" else
                          ("Formula 1", "Motorsport", "Autosport", "RaceFans")[i % 4]
                          if page == "formula1" else page)
                items.append({"id": f"{page}-{i}", "cluster_id": f"{page}-{i}",
                              "cluster_rep": True, "source": source, "category": page,
                              "title": f"{page} story {i}", "score": 6,
                              "published_at": now})
        for i, source in enumerate(("BBC US & Canada", "Financial Times US", "Reuters")):
            items.append({"id": f"world-required-{i}",
                          "cluster_id": f"world-required-{i}", "cluster_rep": True,
                          "source": source, "category": "worldnews",
                          "title": f"{source} headline", "score": 6,
                          "published_at": now})
        for i, source in enumerate(("Brickset", "The Brothers Brick")):
            items.append({"id": f"lego-required-{i}",
                          "cluster_id": f"lego-required-{i}", "cluster_rep": True,
                          "source": source, "category": "technology",
                          "title": f"{source} LEGO headline", "score": 6,
                          "published_at": now})
        sports = [
            ("BBC Football", "football match"), ("BBC Football", "soccer result"),
            ("GE Flamengo", "Flamengo victory"), ("BBC Tennis", "US Open tennis"),
            ("ATP Tour", "ATP tennis result"),
            ("World Surf League", "WSL surf finals"),
            ("Alpinist", "Alpine mountain expedition"),
            ("BBC Tennis", "ATP tennis draw"),
            ("ExplorersWeb", "Mountain summit expedition"),
        ]
        for i, (source, title) in enumerate(sports):
            items.append({"id": f"sports-{i}", "cluster_id": f"sports-{i}",
                          "cluster_rep": True, "source": source, "category": "sports",
                          "title": title, "score": 6, "published_at": now})
        selected, gaps = pipeline.select_balanced_issue(items)
        counts = {}
        for item in selected:
            counts[item["category"]] = counts.get(item["category"], 0) + 1
        for page, (minimum, maximum) in pipeline.PAGE_BUDGETS.items():
            self.assertGreaterEqual(counts.get(page, 0), minimum)
            self.assertLessEqual(counts.get(page, 0), maximum)
        self.assertEqual([], gaps)

    def test_f1_desk_balances_sources_and_reporting_kinds(self):
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        titles = [
            "Italian GP practice results", "Qualifying live classification", "Updated F1 standings",
            "Ferrari engine upgrade explained", "How the new floor changes aero",
            "Weather forecast for the Grand Prix weekend", "Team announces new principal",
            "Driver contract confirmed", "Race director issues bulletin", "Paddock analysis",
            "Driver reveals future plans", "Interview: why the season matters",
        ]
        sources = ["Formula 1", "Motorsport", "Autosport", "RaceFans", "The Race"]
        for i, title in enumerate(titles):
            rows.append({"id": f"f1-{i}", "cluster_id": f"f1-{i}", "cluster_rep": True,
                         "source": sources[i % len(sources)], "category": "formula1",
                         "title": title, "score": 20-i, "published_at": now})
        selected, _ = pipeline.select_balanced_issue(rows)
        kinds = {item.get("f1_kind") for item in selected}
        self.assertEqual(12, len(selected))
        self.assertTrue({"results_updates", "technical", "preview_forecast", "news"} <= kinds)
        self.assertLessEqual(sum(item["source"] == "Formula 1" for item in selected), 3)

    def test_balanced_issue_reports_missing_sports_subtopic(self):
        now = datetime.now(timezone.utc).isoformat()
        football = [{"id": f"f{i}", "cluster_id": f"f{i}", "cluster_rep": True,
                     "source": "BBC Football", "category": "sports",
                     "title": "Football", "score": 10, "published_at": now}
                    for i in range(20)]
        selected, gaps = pipeline.select_balanced_issue(football)
        self.assertLessEqual(len(selected), pipeline.SPORTS_MAXIMUMS["football"])
        missing = {gap.get("subtopic") for gap in gaps}
        self.assertTrue({"tennis", "surf", "mountaineering"} <= missing)

    def test_named_sources_are_protected_before_page_budgets(self):
        now = datetime.now(timezone.utc).isoformat()
        items = [{"id": f"bbc-{i}", "cluster_id": f"bbc-{i}",
                  "cluster_rep": True, "source": "BBC", "category": "worldnews",
                  "title": f"World {i}", "score": 10, "published_at": now}
                 for i in range(12)]
        required = (("BBC US & Canada", "worldnews"),
                    ("Financial Times US", "worldnews"),
                    ("Reuters", "worldnews"),
                    ("ATP Tour", "sports"),
                    ("World Surf League", "sports"),
                    ("Brickset", "technology"),
                    ("The Brothers Brick", "technology"))
        for i, (source, page) in enumerate(required):
            items.append({"id": f"named-{i}", "cluster_id": f"named-{i}",
                          "cluster_rep": True, "source": source, "category": page,
                          "title": source, "score": 1, "published_at": now})
        selected, _ = pipeline.select_balanced_issue(items)
        sources = {item["source"] for item in selected}
        self.assertTrue({"BBC US & Canada", "Financial Times US", "Reuters",
                         "ATP Tour", "World Surf League", "Brickset",
                         "The Brothers Brick"} <= sources)

    def test_brickset_random_daily_filler_is_filtered(self):
        rules = {"Brickset": {"exclude_any": ["random set of the day",
                                                  "random figure of the day"]}}
        useful = {"source": "Brickset", "title": "LEGO 72306 PlayStation revealed!"}
        filler = {"source": "Brickset", "title": "Random set of the day: Blaster Bike"}
        self.assertTrue(pipeline.apply_source_scope(useful, rules))
        self.assertFalse(pipeline.apply_source_scope(filler, rules))

    def test_durable_pages_receive_longer_windows(self):
        self.assertGreaterEqual(pipeline._page_window_hours("ideas", 36), 24 * 14)
        self.assertGreaterEqual(pipeline._page_window_hours("comics", 36), 24 * 365)
        self.assertEqual(36, pipeline._page_window_hours("unknown", 36))

    def test_comics_keeps_only_latest_from_each_named_series(self):
        items = [
            {"id": "g-old", "cluster_id": "g-old", "cluster_rep": True,
             "source": "GiantITP", "category": "comics", "title": "Old G",
             "score": 6, "published_at": "2026-01-01T00:00:00+00:00"},
            {"id": "g-new", "cluster_id": "g-new", "cluster_rep": True,
             "source": "GiantITP", "category": "comics", "title": "New G",
             "score": 6, "published_at": "2026-02-01T00:00:00+00:00"},
            {"id": "w-old", "cluster_id": "w-old", "cluster_rep": True,
             "source": "Wilde Life", "category": "comics", "title": "Old W",
             "score": 6, "published_at": "2025-01-01T00:00:00+00:00"},
            {"id": "w-new", "cluster_id": "w-new", "cluster_rep": True,
             "source": "Wilde Life", "category": "comics", "title": "New W",
             "score": 6, "published_at": "2025-02-01T00:00:00+00:00"},
        ]
        selected, gaps = pipeline.select_balanced_issue(items)
        self.assertEqual({"g-new", "w-new"}, {item["id"] for item in selected})
        self.assertNotIn("comics", {gap.get("page") for gap in gaps})

    def test_same_source_cluster_gets_no_corroboration_boost(self):
        items = [
            {"id": "a", "title": "Daily weather forecast São Paulo", "source": "Globo",
             "score": 6, "embedding": None},
            {"id": "b", "title": "Daily weather forecast Rio", "source": "G1 Brasil",
             "score": 6, "embedding": None},
        ]
        clustered = pipeline.cluster(items)
        self.assertTrue(any(item["cluster_size"] == 2 for item in clustered))
        self.assertTrue(all(item["cluster_boost"] == 0 for item in clustered))

    def test_retention_preserves_sources_before_high_volume_backfill(self):
        now = datetime.now(timezone.utc).isoformat()
        items = []
        for i in range(40):
            items.append({"id": f"loud-{i}", "cluster_id": f"loud-{i}",
                          "source": "Loud", "score": 6, "published_at": now})
        for i in range(8):
            items.append({"id": f"quiet-{i}", "cluster_id": f"quiet-{i}",
                          "source": f"Quiet {i}", "score": 6, "published_at": now})
        cfg = {"retain_ceiling": 20, "retain_floor": 10,
               "retain_base_ttl_hours": 24, "retain_max_ttl_hours": 72,
               "retain_hard_max_age_hours": 120}
        retained = pipeline.apply_retention(items, cfg)
        sources = {item["source"] for item in retained}
        self.assertTrue({f"Quiet {i}" for i in range(8)} <= sources)
        self.assertLessEqual(sum(item["source"] == "Loud" for item in retained), 12)

    def test_durable_idea_survives_breaking_news_ttl(self):
        published = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        item = {"id": "idea", "cluster_id": "idea", "source": "Aeon",
                "category": "ideas", "score": 6, "published_at": published}
        cfg = {"retain_ceiling": 20, "retain_floor": 1,
               "retain_base_ttl_hours": 24, "retain_max_ttl_hours": 72,
               "retain_hard_max_age_hours": 120}
        self.assertEqual([item], pipeline.apply_retention([item], cfg))


if __name__ == "__main__":
    unittest.main()
