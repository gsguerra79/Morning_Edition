import unittest
from datetime import datetime, timedelta, timezone

import pipeline


class PipelineDiversityTests(unittest.TestCase):
    def test_durable_pages_receive_longer_windows(self):
        self.assertGreaterEqual(pipeline._page_window_hours("ideas", 36), 24 * 14)
        self.assertEqual(36, pipeline._page_window_hours("unknown", 36))

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
