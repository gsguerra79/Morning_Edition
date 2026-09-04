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


if __name__ == '__main__':
    unittest.main()
