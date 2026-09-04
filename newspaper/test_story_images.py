import json
import unittest
from unittest.mock import patch

import server


class _Response:
    def __init__(self, body, url='https://news.google.com/search'):
        self._body = body.encode('utf-8') if isinstance(body, str) else body
        self._url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit=None):
        return self._body if limit is None else self._body[:limit]

    def geturl(self):
        return self._url


class StoryImageTests(unittest.TestCase):
    def test_direct_article_metadata_returns_exact_publisher_art(self):
        page = ('<meta property="og:image" '
                'content="https://media.formula1.com/image/upload/story.webp">')
        response = _Response(page, 'https://www.formula1.com/en/latest/article/story')
        with patch('server.urllib.request.urlopen', return_value=response):
            self.assertEqual(
                'https://media.formula1.com/image/upload/story.webp',
                server._direct_story_image('https://www.formula1.com/en/latest/article/story'))

    def test_redirect_to_non_publisher_page_is_not_used(self):
        page = ('<meta property="og:image" '
                'content="https://images.ft.com/v3/image/raw/logo">')
        response = _Response(page, 'https://access-error.example/story')
        with patch('server.urllib.request.urlopen', return_value=response):
            self.assertIsNone(
                server._direct_story_image('https://www.ft.com/content/story'))

    def test_arbitrary_source_cannot_trigger_story_fetch(self):
        with self.assertRaisesRegex(ValueError, 'not eligible'):
            server.fetch_story_image('Unknown', 'A headline', 'https://example.com/story')

    def test_reuters_mobile_image_requires_exact_canonical_article(self):
        blocks = [{
            'type': 'article_detail',
            'data': {'article': {
                'canonical_url': '/world/exact-story-2026-09-04/',
                'title': 'Exact story',
                'thumbnail': {
                    'resizer_url': 'https://www.reuters.com/resizer/v2/EXACT.jpg?auth=x',
                },
            }},
        }]
        response = _Response(json.dumps(blocks),
                             'https://www.reuters.com/mobile/v1/world/exact-story-2026-09-04/')
        with patch('server.urllib.request.urlopen', return_value=response):
            self.assertEqual(
                'https://www.reuters.com/resizer/v2/EXACT.jpg?auth=x',
                server._reuters_mobile_story_image(
                    'https://www.reuters.com/world/exact-story-2026-09-04/',
                    'Earlier version of the headline - Reuters'))

    def test_reuters_mobile_image_rejects_nearby_article_art(self):
        blocks = [{
            'type': 'article_detail',
            'data': {'article': {
                'canonical_url': '/world/other-story-2026-09-04/',
                'title': 'Other story',
                'thumbnail': {
                    'resizer_url': 'https://www.reuters.com/resizer/v2/WRONG.jpg?auth=x',
                },
            }},
        }]
        response = _Response(json.dumps(blocks))
        with patch('server.urllib.request.urlopen', return_value=response):
            self.assertIsNone(server._reuters_mobile_story_image(
                'https://www.reuters.com/world/exact-story-2026-09-04/',
                'Exact story'))

    def test_reuters_default_logo_is_not_treated_as_article_art(self):
        blocks = [{
            'type': 'article_detail',
            'data': {'article': {
                'canonical_url': '/world/exact-story-2026-09-04/',
                'title': 'Exact story',
                'thumbnail': {
                    'resizer_url': 'https://www.reuters.com/resizer/v2/LOGO.png?auth=x',
                    'alt_text': 'Reuters logo',
                    'subtitle': 'TOPIC:DEFAULT_TOPIC_THUMBNAIL',
                },
            }},
        }]
        response = _Response(json.dumps(blocks))
        with patch('server.urllib.request.urlopen', return_value=response):
            self.assertIsNone(server._reuters_mobile_story_image(
                'https://www.reuters.com/world/exact-story-2026-09-04/',
                'Exact story'))

    def test_signed_google_feed_item_resolves_only_its_reuters_url(self):
        page = ('<div data-n-a-id="signed-id" data-n-a-ts="123" '
                'data-n-a-sg="signed-token"></div>')
        result = json.dumps([['wrb.fr', 'Fbv4je', json.dumps([
            'garturlres', 'https://www.reuters.com/world/exact-story-2026-09-04/', 1
        ])]])
        with patch('server.urllib.request.urlopen', side_effect=[
                _Response(page), _Response(result)]):
            self.assertEqual(
                'https://www.reuters.com/world/exact-story-2026-09-04/',
                server._decode_google_news_article(
                    'https://news.google.com/rss/articles/signed-id?oc=5'))

    def test_signed_google_feed_item_rejects_non_reuters_target(self):
        page = ('<div data-n-a-id="signed-id" data-n-a-ts="123" '
                'data-n-a-sg="signed-token"></div>')
        result = json.dumps([['wrb.fr', 'Fbv4je', json.dumps([
            'garturlres', 'https://unrelated.example/wrong-story', 1
        ])]])
        with patch('server.urllib.request.urlopen', side_effect=[
                _Response(page), _Response(result)]):
            self.assertIsNone(server._decode_google_news_article(
                'https://news.google.com/rss/articles/signed-id?oc=5'))


if __name__ == '__main__':
    unittest.main()
