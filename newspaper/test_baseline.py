import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import editions
import server


class BaselineRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        editions.EDITIONS_DIR = self.tmp.name
        self.now = datetime(2026, 8, 29, 7, 30,
                            tzinfo=ZoneInfo("America/Chicago"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_existing_edition_is_byte_immutable_without_force(self):
        first = editions.publish(
            {"articles": [{"id": "a", "cluster_id": "story-a"}]},
            "morning", self.now)
        path = Path(self.tmp.name) / "2026-08-29-morning.json"
        before = path.read_bytes()

        second = editions.publish(
            {"articles": [{"id": "replacement", "cluster_id": "story-b"}]},
            "morning", self.now)

        self.assertEqual(first, second)
        self.assertEqual(before, path.read_bytes())

    def test_legacy_state_payload_receives_current_defaults(self):
        legacy = {
            "readIds": ["read-1"],
            "later": [{"id": "saved-1"}],
            "history": [],
            "viewState": {"currentView": "later"},
        }

        normalized = server.normalize_payload(legacy)

        self.assertEqual(["read-1"], normalized["readIds"])
        self.assertEqual([{"id": "saved-1"}], normalized["later"])
        self.assertEqual([], normalized["feedback"])
        self.assertEqual("later", normalized["viewState"]["currentView"])
        self.assertEqual("all", normalized["viewState"]["currentCat"])
        self.assertFalse(normalized["viewState"]["showScores"])
        self.assertEqual({}, normalized["sourceStats"])
        self.assertEqual({"lastDecayAt": None}, normalized["learning"])

    def test_feedback_is_persisted_and_malformed_entries_are_removed(self):
        normalized = server.normalize_payload({
            "readIds": ["story-1"],
            "feedback": [
                {"id": "story-1", "reason": "wrong_topic"},
                {"reason": "missing id"},
            ],
        })
        pruned = server.prune(normalized)
        self.assertEqual(
            [{"id": "story-1", "reason": "wrong_topic"}],
            pruned["feedback"],
        )

    def test_unknown_legacy_fields_are_not_persisted(self):
        normalized = server.normalize_payload({"readIds": [], "obsolete": 1})
        self.assertNotIn("obsolete", normalized)

    def test_home_topics_use_full_width_reflow_and_render_every_selected_card(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("className = 'topic-sections'", html)
        self.assertIn("section.articles.map(gridCardHTML)", html)
        self.assertIn("balancedTopicColumns(section.articles.length)", html)
        self.assertNotIn("section.articles.slice(1, 5)", html)

    def test_weather_desk_and_masthead_timestamp_are_present(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn('id="vnav-weather"', html)
        self.assertIn('id="view-weather"', html)
        self.assertIn("const WEATHER_URL       = '/weather';", html)
        self.assertIn("Seven-day forecast", html)
        self.assertIn("Hourly forecast · next 24 hours", html)
        self.assertIn("Houston radar", html)
        self.assertIn("Rio de Janeiro, Brazil", html)
        self.assertIn("Updated ${issueTime}", html)


if __name__ == "__main__":
    unittest.main()
