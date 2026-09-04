import json
import os
import tempfile
import unittest
from unittest import mock
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
        self.assertFalse(normalized["viewState"]["hideReadOnOpen"])
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
        self.assertIn("grid-auto-flow: row dense", html)
        self.assertIn("escapeAttr(a.summary)", html)

    def test_comic_cards_use_artwork_crop_styling(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("comic-card .thumb img", html)
        self.assertIn("a.category === 'comics' ? ' comic-card'", html)
        self.assertIn("/comic-image?url=", html)
        self.assertIn("a.category !== 'comics'", html)

    def test_comic_image_relay_rejects_non_subscribed_hosts(self):
        with self.assertRaisesRegex(ValueError, "not allow-listed"):
            server.fetch_comic_image("https://example.com/comics/page.png")
        with self.assertRaisesRegex(ValueError, "not allow-listed"):
            server.fetch_comic_image("http://i.giantitp.com/comics/oots/page.png")

    def test_news_image_relay_only_allows_ft_and_reuters_cdn_paths(self):
        with self.assertRaisesRegex(ValueError, "not allow-listed"):
            server.fetch_card_image("https://example.com/photo.jpg")
        with self.assertRaisesRegex(ValueError, "not allow-listed"):
            server.fetch_card_image("https://www.reuters.com/world/story")

    def test_reuters_sitemap_feed_format_survives_management_api(self):
        with mock.patch.object(server, 'allowed_categories', return_value={'world'}):
            feed, error = server.normalize_feed_payload({
                'url': 'https://www.reuters.com/arc/outboundfeeds/news-sitemap/?outputType=xml',
                'source': 'Reuters',
                'category': 'world',
                'format': 'reuters_sitemap',
            })
        self.assertIsNone(error)
        self.assertEqual('reuters_sitemap', feed['format'])

    def test_visible_cards_omit_selection_explanation(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertNotIn("Why it’s here:", html)
        self.assertNotIn("whyLine(", html)
        self.assertIn("why_selected", (Path(__file__).parent / "pipeline.py").read_text())

    def test_home_is_stable_and_hot_metal_is_separate(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("const DIGEST_URL        = '/editions/today'", html)
        self.assertIn("const HOT_METAL_URL     = '/hot-metal'", html)
        self.assertIn('Hot Metal', html)
        self.assertNotIn('Live Preview', html)

    def test_live_desks_share_one_payload_between_home_and_detail(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("const LIVE_DESKS_URL    = '/live-desks'", html)
        self.assertIn("function currentDeskArticlePool()", html)
        self.assertIn("liveF1FrontIds.map(id => byId.get(id))", html)
        self.assertIn("liveComicsArticles", html)
        self.assertIn("Live desk · updated", html)

    def test_comics_ignore_hide_after_open_preference(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("article?.category !== 'comics'", html)
        self.assertIn("member?.category !== 'comics'", html)
        self.assertIn("article.category !== 'comics' && sharedState.viewState.hideReadOnOpen", html)

    def test_ft_and_reuters_have_source_art_when_story_image_is_absent(self):
        root = Path(__file__).parent
        html = (root / "digest.html").read_text(encoding="utf-8")
        dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("'/ft-card.svg?v=1'", html)
        self.assertIn("'/reuters-card.svg?v=1'", html)
        self.assertIn('ft-card.svg', server.ICON_FILES)
        self.assertIn('reuters-card.svg', server.ICON_FILES)
        self.assertIn('ft-card.svg reuters-card.svg', dockerfile)

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

    def test_sources_owns_feed_and_topic_management(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("['feeds', 'Manage sources']", html)
        self.assertIn("['topics', 'Topics']", html)
        self.assertNotIn("{ id: 'feeds',      label: 'Feeds' }", html)
        self.assertNotIn("{ id: 'categories', label: 'Categories' }", html)

    def test_opened_story_visibility_is_optional_and_defaults_to_visible(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("hideReadOnOpen: false", html)
        self.assertIn("Hide stories after opening", html)

    def test_forge_favicon_is_versioned_and_shipped(self):
        root = Path(__file__).parent
        html = (root / "digest.html").read_text(encoding="utf-8")
        svg = (root / "favicon.svg").read_text(encoding="utf-8")
        dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn('/favicon.svg?v=forge-1', html)
        self.assertIn('hammer and anvil', svg)
        self.assertIn("favicon.svg", server.ICON_FILES)
        self.assertEqual('image/svg+xml', server.STATIC_TYPES['.svg'])
        self.assertIn('favicon.svg favicon.ico', dockerfile)

    def test_f1_page_has_single_session_frame_sticky_standings_and_news_tiers(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("const shown = isLive ? liveResult : openF1IsNewer ? liveResult : result", html)
        self.assertIn("f1-session-panel", html)
        self.assertIn("f1-standings-rail", html)
        self.assertIn(".rail-col { min-width:0; position:sticky", html)
        self.assertIn("grid-template-columns:1fr", html)
        self.assertIn("'Race desk'", html)
        self.assertIn("'Paddock & off-track'", html)
        self.assertIn("Updates · Strategy · Personnel · Technical · News", html)
        self.assertIn("Interviews · Personal · Rumours · Tangential", html)


if __name__ == "__main__":
    unittest.main()
