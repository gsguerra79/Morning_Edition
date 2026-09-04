import unittest
from datetime import datetime, timezone

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

    def test_reuters_sitemap_supplies_canonical_story_and_image(self):
        markup = '''
        <urlset xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
          <url>
            <loc>https://www.reuters.com/world/example-story-2026-09-04/</loc>
            <news:news><news:publication_date>2026-09-04T12:00:00Z</news:publication_date>
            <news:title><![CDATA[Example world story]]></news:title></news:news>
            <image:image><image:loc>https://www.reuters.com/resizer/v2/photo.jpg?width=1920&amp;smart=true</image:loc></image:image>
          </url>
          <url><loc>https://www.reuters.com/business/ignored-2026-09-04/</loc>
            <lastmod>2026-09-04T12:00:00Z</lastmod><news:title>Ignored</news:title></url>
        </urlset>'''
        items = pipeline.parse_reuters_sitemap(
            markup, 'Reuters', 'worldnews',
            datetime(2026, 9, 3, tzinfo=timezone.utc))
        self.assertEqual(1, len(items))
        self.assertEqual('Example world story', items[0]['title'])
        self.assertEqual(
            'https://www.reuters.com/resizer/v2/photo.jpg?width=1920&smart=true',
            items[0]['feed_image'])


if __name__ == "__main__":
    unittest.main()
