import unittest

from editorial_selection import select_issue


def article(number, source="Source", category="world", score=5, title=None):
    return {"id": f"a-{number}", "cluster_id": f"c-{number}", "cluster_rep": True,
            "source": source, "category": category, "score": score,
            "title": title or f"Story {number}", "summary": "Summary"}


class EditorialSelectionTests(unittest.TestCase):
    def test_issue_is_bounded_and_source_capped(self):
        items = [article(i, source="Loud", score=100-i) for i in range(30)]
        items += [article(100+i, source=f"Other {i}", score=50-i) for i in range(20)]
        selected, report = select_issue(items, max_stories=20, source_share=.2,
                                        page_caps={"world": 20})
        self.assertEqual(20, len(selected))
        self.assertLessEqual(report["source_counts"]["Loud"], 4)

    def test_must_include_bypasses_normal_caps(self):
        items = [article(i, source="Required", title=f"Major result {i}") for i in range(3)]
        rules = {"sources": {"Required": {"must_any": ["major result"]}}}
        selected, report = select_issue(items, rules=rules, max_stories=1)
        self.assertEqual(3, len(selected))
        self.assertEqual(3, report["mandatory_stories"])
        self.assertTrue(all(item["why_selected"].startswith("Must include") for item in selected))

    def test_avoid_rule_and_exception(self):
        items = [article(1, title="Routine phone deal"),
                 article(2, title="Unusual prototype phone deal")]
        rules = {"sources": {"Source": {"exclude_any": ["phone deal"],
                                           "exclude_unless_any": ["unusual prototype"]}}}
        selected, report = select_issue(items, rules=rules, max_stories=10,
                                        page_caps={"world": 10})
        self.assertEqual(["a-2"], [item["id"] for item in selected])
        self.assertEqual("source_avoid_rule", report["rejected"][0]["code"])

    def test_variant_rule_overrides_canonical_source_rule(self):
        items = [article(1, source="BBC US & Canada", category="worldnews",
                         title="Routine local murder trial"),
                 article(2, source="BBC World", category="worldnews",
                         title="Government announces national policy")]
        registry = {"sources": [{"source": "BBC", "topics": ["World News"]}]}
        rules = {"sources": {"BBC": {}, "BBC US & Canada": {"exclude_any": ["murder"]}}}
        selected, _ = select_issue(items, registry=registry, rules=rules,
                                   max_stories=10, source_share=1)
        self.assertEqual(["a-2"], [item["id"] for item in selected])

    def test_required_scope_defaults_to_empty_instead_of_filler(self):
        items = [article(1, source="Globo", title="Weather today in Brasília"),
                 article(2, source="Globo", title="Federal government announces national policy")]
        rules = {"sources": {"Globo": {"require_any": ["federal government", "rio de janeiro"]}}}
        selected, report = select_issue(items, rules=rules, max_stories=10,
                                        page_caps={"world": 10})
        self.assertEqual(["a-2"], [item["id"] for item in selected])
        self.assertEqual("outside_source_scope", report["rejected"][0]["code"])

    def test_repeated_input_is_deterministic(self):
        items = [article(i, source=f"Source {i % 3}", score=5) for i in range(12)]
        first, first_report = select_issue(items, max_stories=8, page_caps={"world": 8})
        second, second_report = select_issue(items, max_stories=8, page_caps={"world": 8})
        self.assertEqual(first, second)
        self.assertEqual(first_report, second_report)

    def test_representative_morning_fixture_is_in_target_band(self):
        caps = {"technology": 10, "photography": 5, "outdoors": 5,
                "f1": 6, "world": 8, "comics": 2}
        items = []
        number = 0
        for page, cap in caps.items():
            for offset in range(cap + 3):
                source = (("GiantITP", "Wilde Life")[offset % 2]
                          if page == "comics" else f"Source {offset % 8}")
                items.append(article(number, source=source,
                                     category=page, score=100-number/100))
                number += 1
        selected, report = select_issue(items, max_stories=40, source_share=.20)
        self.assertGreaterEqual(len(selected), 30)
        self.assertLessEqual(len(selected), 45)
        self.assertEqual(caps, report["page_counts"])
        self.assertLessEqual(max(report["source_counts"].values()), 8)

    def test_empty_input_is_honestly_empty(self):
        selected, report = select_issue([], max_stories=40)
        self.assertEqual([], selected)
        self.assertEqual(0, report["selected_stories"])

    def test_cluster_members_do_not_duplicate_story(self):
        rep = dict(article(1), url="https://primary.example/story")
        member = dict(rep, id="member", cluster_rep=False, source="Other",
                      url="https://other.example/story")
        selected, _ = select_issue([rep, member], max_stories=10,
                                   page_caps={"world": 10})
        self.assertEqual(["a-1"], [item["id"] for item in selected])
        self.assertEqual("Other", selected[0]["corroborating_sources"][0]["source"])

    def test_same_source_cluster_is_not_presented_as_corroboration(self):
        registry = {"sources": [{"source": "Globo", "what_i_read": "Federal news"}]}
        rep = dict(article(1, source="Globo"), url="https://g1.example/story")
        member = dict(rep, id="member", cluster_rep=False, source="G1 Brasil",
                      url="https://g1.example/rewrite")
        selected, _ = select_issue([rep, member], registry=registry, max_stories=10,
                                   page_caps={"world": 10})
        self.assertNotIn("corroborating_sources", selected[0])
        self.assertNotIn("independent", selected[0]["why_selected"].lower())

    def test_named_world_and_sports_sources_survive_page_caps(self):
        items = [article(i, source="BBC World", category="worldnews", score=100-i)
                 for i in range(8)]
        items += [
            article(20, source="BBC US & Canada", category="worldnews", score=1),
            article(21, source="Financial Times US", category="worldnews", score=1),
            article(22, source="Reuters", category="worldnews", score=1),
            article(23, source="ATP Tour", category="sports", score=1),
            article(24, source="World Surf League", category="sports", score=1),
        ]
        selected, _ = select_issue(items, max_stories=20, source_share=1,
                                   page_caps={"worldnews": 8, "sports": 5})
        sources = {item["source"] for item in selected}
        self.assertTrue({"BBC US & Canada", "Financial Times US", "Reuters",
                         "ATP Tour", "World Surf League"} <= sources)

    def test_comics_shows_only_latest_from_each_series(self):
        items = [
            dict(article(1, source="GiantITP", category="comics"),
                 published_at="2026-01-01T00:00:00+00:00"),
            dict(article(2, source="GiantITP", category="comics"),
                 published_at="2026-02-01T00:00:00+00:00"),
            dict(article(3, source="Wilde Life", category="comics"),
                 published_at="2025-01-01T00:00:00+00:00"),
            dict(article(4, source="Wilde Life", category="comics"),
                 published_at="2025-02-01T00:00:00+00:00"),
        ]
        selected, _ = select_issue(items, max_stories=10, source_share=1,
                                   page_caps={"comics": 2})
        self.assertEqual({"a-2", "a-4"}, {item["id"] for item in selected})

    def test_default_page_caps_match_balanced_retained_issue(self):
        page_counts = {"brazilnews": 6, "worldnews": 8, "formula1": 6,
                       "technology": 10, "comics": 2, "sports": 12, "ideas": 5}
        items = []
        number = 0
        for page, count in page_counts.items():
            for offset in range(count):
                if page == "comics":
                    source = ("GiantITP", "Wilde Life")[offset]
                elif page == "worldnews":
                    source = ("BBC US & Canada" if offset < 3 else
                              "Reuters" if offset < 7 else "Financial Times US")
                elif page == "sports":
                    source = ("World Surf League" if offset < 3 else
                              "ATP Tour" if offset < 5 else f"Sports Source {offset}")
                else:
                    source = f"{page} Source {offset}"
                items.append(article(number, source=source, category=page,
                                     score=100-number/100))
                number += 1
        selected, report = select_issue(items)
        self.assertEqual(49, len(selected))
        self.assertEqual(page_counts, report["page_counts"])
        self.assertFalse(any(item["code"] == "page_cap" for item in report["rejected"]))


if __name__ == "__main__":
    unittest.main()
