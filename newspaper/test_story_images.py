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
    def test_ft_search_returns_only_exact_result_publisher_art(self):
        title = 'Labour working'
        image = ('https://images.ft.com/v3/image/raw/'
                 'https%3A%2F%2Fexample.test%2Fstory.jpg?source\\u003dnext-article'
                 '\\u0026width\\u003d700')
        page = '<script>' + title + ' ' + image + '</script>'
        with patch('server.urllib.request.urlopen', return_value=_Response(page)):
            result = server._google_news_story_image(title, 'Financial Times US')
        self.assertEqual(
            'https://images.ft.com/v3/image/raw/'
            'https%3A%2F%2Fexample.test%2Fstory.jpg?source=next-article&width=700',
            result)

    def test_search_does_not_accept_generic_google_thumbnail(self):
        page = ('<script>Labour working '
                'https://lh3.googleusercontent.com/unrelated=s0-w300</script>')
        with patch('server.urllib.request.urlopen', return_value=_Response(page)):
            self.assertIsNone(
                server._google_news_story_image('Labour working', 'Financial Times US'))

    def test_arbitrary_source_cannot_trigger_story_fetch(self):
        with self.assertRaisesRegex(ValueError, 'not eligible'):
            server.fetch_story_image('Unknown', 'A headline', 'https://example.com/story')


if __name__ == '__main__':
    unittest.main()
