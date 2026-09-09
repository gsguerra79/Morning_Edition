import unittest
from pathlib import Path


class SportsLabelTests(unittest.TestCase):
    def test_sports_cards_show_descriptive_subtopic_labels(self):
        html = (Path(__file__).parent / "digest.html").read_text(encoding="utf-8")
        self.assertIn("function sportsArticleClass(a)", html)
        self.assertIn("football:'Football'", html)
        self.assertIn("tennis:'Tennis'", html)
        self.assertIn("surf:'Surfing'", html)
        self.assertIn("mountaineering:'Mountaineering'", html)
        self.assertIn("adventure:'Adventure'", html)


if __name__ == "__main__":
    unittest.main()
