import unittest

import pipeline


class PageMediaTests(unittest.TestCase):
    def test_giantitp_comic_art_is_used_when_open_graph_image_is_absent(self):
        markup = '''
          <img src="https://i.giantitp.com/redesign/Header_Comics.gif">
          <td><img src="https://i.giantitp.com/comics/oots/oots1340_hash.png"></td>
        '''
        self.assertEqual(
            "https://i.giantitp.com/comics/oots/oots1340_hash.png",
            pipeline._page_image(markup, "https://www.giantitp.com/comics/oots1340.html"),
        )

    def test_wilde_life_comic_art_is_used_when_open_graph_image_is_absent(self):
        markup = '<img title="Panel" src="/comics/1788335762-1641.png" id="cc-comic">'
        self.assertEqual(
            "https://www.wildelifecomic.com/comics/1788335762-1641.png",
            pipeline._page_image(markup, "https://www.wildelifecomic.com/comic/1641"),
        )

    def test_open_graph_image_still_takes_precedence(self):
        markup = '<meta property="og:image" content="/images/story.jpg">'
        self.assertEqual(
            "https://example.com/images/story.jpg",
            pipeline._page_image(markup, "https://example.com/news/item"),
        )


if __name__ == "__main__":
    unittest.main()
