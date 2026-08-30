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

    def test_repeated_input_is_deterministic(self):
        items = [article(i, source=f"Source {i % 3}", score=5) for i in range(12)]
        first, first_report = select_issue(items, max_stories=8, page_caps={"world": 8})
        second, second_report = select_issue(items, max_stories=8, page_caps={"world": 8})
        self.assertEqual(first, second)
        self.assertEqual(first_report, second_report)

    def test_representative_morning_fixture_is_in_target_band(self):
        caps = {"technology": 8, "photography": 5, "outdoors": 5,
                "f1": 6, "world": 8, "comics": 2}
        items = []
        number = 0
        for page, cap in caps.items():
            for offset in range(cap + 3):
                items.append(article(number, source=f"Source {offset % 8}",
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


if __name__ == "__main__":
    unittest.main()
