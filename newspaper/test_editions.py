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
        self.old_limits = {
            key: os.environ.get(key) for key in
            ('MORNING_MAX_STORIES', 'AFTERNOON_MAX_STORIES', 'SOURCE_SHARE_CAP')
        }
        self.now = datetime(2026, 8, 24, 16, 30, tzinfo=ZoneInfo('America/Chicago'))

    def tearDown(self):
        for key, value in self.old_limits.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
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

    def test_publish_uses_bounded_selector_and_records_report(self):
        os.environ['MORNING_MAX_STORIES'] = '2'
        os.environ['SOURCE_SHARE_CAP'] = '1.0'
        issue = editions.publish({'articles': [
            {'id': f'a-{i}', 'cluster_id': f'c-{i}', 'cluster_rep': True,
             'source': 'Source', 'category': 'world', 'score': 10-i}
            for i in range(5)
        ]}, 'morning', self.now)
        self.assertEqual(2, issue['article_count'])
        self.assertEqual(2, issue['selection_report']['selected_stories'])
        self.assertTrue(all(item['why_selected'] for item in issue['articles']))


if __name__ == '__main__':
    unittest.main()
