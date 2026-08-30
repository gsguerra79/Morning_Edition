import unittest

from story_identity import annotate, classify, classify_afternoon, normalize_url


def story(identifier, title, summary="", url="https://example.com/story"):
    return {"id": identifier, "title": title, "summary": summary, "url": url,
            "source": "Source", "category": "world", "cluster_rep": True, "score": 8}


class StoryIdentityTests(unittest.TestCase):
    def test_url_normalization_removes_tracking_and_cosmetic_variants(self):
        left = normalize_url("http://www.example.com/news/item/?utm_source=x&b=2&a=1#top")
        right = normalize_url("https://example.com/news/item?a=1&b=2")
        self.assertEqual(right, left)

    def test_malformed_url_does_not_break_publication(self):
        self.assertEqual("", normalize_url("http://example.com:not-a-port/story"))

    def test_feed_id_and_cluster_changes_do_not_change_fingerprint(self):
        first = annotate(story("old", "Ferrari announces 2027 Formula 1 driver"))
        second = annotate(story("new", "Ferrari announces 2027 Formula 1 driver") |
                          {"cluster_id": "different"})
        self.assertEqual(first["story_fingerprint"], second["story_fingerprint"])

    def test_headline_rewrite_is_rejected_as_unchanged(self):
        morning = annotate(story("am", "Ferrari expected to sign Brazilian driver"))
        afternoon = story("pm", "Brazilian driver reportedly expected to sign for Ferrari",
                          url="https://example.com/rewritten-story")
        result = classify(afternoon, [morning])
        self.assertEqual("unchanged", result["change_class"])
        self.assertEqual("title_overlap", result["match_method"])

    def test_rumor_becoming_confirmed_is_material(self):
        morning = annotate(story("am", "Ferrari rumored to sign Brazilian driver"))
        afternoon = story("pm", "Ferrari officially confirmed Brazilian driver signs")
        result = classify(afternoon, [morning])
        self.assertEqual("material_update", result["change_class"])
        self.assertEqual("status_confirmed", result["change_reason"])

    def test_correction_is_material(self):
        morning = annotate(story("am", "Agency reports 12 homes damaged"))
        afternoon = story("pm", "Correction: agency reports 12 homes damaged")
        result = classify(afternoon, [morning])
        self.assertEqual("correction_published", result["change_reason"])

    def test_new_numeric_fact_is_material(self):
        morning = annotate(story("am", "Storm damages homes", "Officials assess damage"))
        afternoon = story("pm", "Storm damages homes", "Officials confirm 20 homes damaged")
        result = classify(afternoon, [morning])
        self.assertEqual("new_numeric_fact", result["change_reason"])

    def test_genuinely_new_story_is_included(self):
        result = classify(story("pm", "Quanta explains a new geometry proof",
                                url="https://quanta.example/geometry-proof"), [
            annotate(story("am", "Ferrari announces a new driver"))])
        self.assertEqual("new_story", result["change_class"])

    def test_no_change_report_is_explicit(self):
        morning = annotate(story("am", "Ferrari expected to sign Brazilian driver"))
        included, report = classify_afternoon([
            story("pm", "Brazilian driver expected to sign for Ferrari")], [morning])
        self.assertEqual([], included)
        self.assertEqual(1, report["unchanged_rejected"])


if __name__ == "__main__":
    unittest.main()
