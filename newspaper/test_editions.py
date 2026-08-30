import os
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import editions


class EditionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        editions.EDITIONS_DIR = self.tmp.name
        self.now = datetime(2026, 8, 24, 16, 30, tzinfo=ZoneInfo('America/Chicago'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_afternoon_excludes_morning_stories_and_clusters(self):
        morning = {'articles': [
            {'id': 'a', 'cluster_id': 'story-a', 'category': 'world'},
            {'id': 'b', 'cluster_id': 'story-b', 'category': 'f1'},
        ]}
        editions.publish(morning, 'morning', self.now)
        afternoon = editions.publish({'articles': [
            {'id': 'a', 'cluster_id': 'story-a', 'category': 'world'},
            {'id': 'c', 'cluster_id': 'story-b', 'category': 'f1'},
            {'id': 'd', 'cluster_id': 'story-d', 'category': 'technology'},
        ]}, 'afternoon', self.now)
        self.assertEqual(['d'], [a['id'] for a in afternoon['articles']])
        self.assertIn('Why', 'Why')
        self.assertTrue(afternoon['articles'][0]['why_selected'])

    def test_publish_is_immutable_without_force(self):
        first = editions.publish({'articles': [{'id':'a'}]}, 'morning', self.now)
        second = editions.publish({'articles': [{'id':'b'}]}, 'morning', self.now)
        self.assertEqual(first, second)

    def test_afternoon_sorts_before_morning(self):
        editions.publish({'articles': []}, 'morning', self.now)
        editions.publish({'articles': []}, 'afternoon', self.now)
        self.assertEqual('afternoon', editions.list_editions()[0]['kind'])


if __name__ == '__main__':
    unittest.main()
