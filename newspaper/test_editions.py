import os
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import editions


class EditionTests(unittest.TestCase):
    def test_preview_is_bounded_and_does_not_write_archive(self):
        digest = {'articles': [
            {'id': f'a-{i}', 'cluster_id': f'c-{i}', 'cluster_rep': True,
             'title': f'Story {i}', 'url': f'https://example.com/{i}',
             'source': f'Source {i % 8}', 'category': 'world', 'score': 100-i}
            for i in range(80)
        ]}
        before = list(os.listdir(self.tmp.name))
        result = editions.preview(digest, now=self.now)
        self.assertEqual('live-preview', result['id'])
        self.assertTrue(result['preview'])
        self.assertLessEqual(result['article_count'], 60)
        self.assertEqual(before, list(os.listdir(self.tmp.name)))

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

    def test_material_afternoon_update_links_to_morning_story(self):
        morning = editions.publish({'articles': [{
            'id': 'am', 'title': 'Ferrari rumored to sign Brazilian driver',
            'url': 'https://example.com/f1-driver', 'source': 'Source',
            'category': 'f1', 'cluster_rep': True, 'score': 8,
        }]}, 'morning', self.now)
        afternoon = editions.publish({'articles': [{
            'id': 'pm', 'title': 'Ferrari officially confirmed Brazilian driver signs',
            'url': 'https://example.com/f1-driver?utm_source=feed', 'source': 'Source',
            'category': 'f1', 'cluster_rep': True, 'score': 8,
        }]}, 'afternoon', self.now)
        self.assertEqual(['pm'], [item['id'] for item in afternoon['articles']])
        self.assertEqual(morning['articles'][0]['story_fingerprint'],
                         afternoon['articles'][0]['afternoon_update_of'])
        self.assertEqual('status_confirmed', afternoon['articles'][0]['change_reason'])

    def test_no_change_afternoon_has_explicit_empty_state(self):
        item = {'id': 'same', 'title': 'Agency announces a policy review',
                'url': 'https://example.com/policy', 'source': 'Source',
                'category': 'world', 'cluster_rep': True, 'score': 8}
        editions.publish({'articles': [item]}, 'morning', self.now)
        afternoon = editions.publish({'articles': [dict(item, id='rewrite')]},
                                     'afternoon', self.now)
        self.assertEqual(0, afternoon['article_count'])
        self.assertEqual('no_material_change', afternoon['empty_state']['code'])
        self.assertEqual(1, afternoon['selection_report']['material_change']['unchanged_rejected'])

    def test_unselected_morning_candidate_cannot_become_stale_afternoon_filler(self):
        os.environ['MORNING_MAX_STORIES'] = '1'
        os.environ['SOURCE_SHARE_CAP'] = '1.0'
        candidates = [
            {'id': 'top', 'title': 'Top morning story', 'url': 'https://example.com/top',
             'source': 'Source', 'category': 'world', 'cluster_rep': True, 'score': 9},
            {'id': 'overflow', 'title': 'Morning overflow story',
             'url': 'https://example.com/overflow', 'source': 'Source',
             'category': 'world', 'cluster_rep': True, 'score': 8},
        ]
        morning = editions.publish({'articles': candidates}, 'morning', self.now)
        self.assertEqual(1, morning['article_count'])
        self.assertEqual(2, len(morning['candidate_story_index']))
        afternoon = editions.publish({'articles': [dict(candidates[1], id='rewritten')]},
                                     'afternoon', self.now)
        self.assertEqual(0, afternoon['article_count'])
        self.assertEqual('no_material_change', afternoon['empty_state']['code'])

    def test_new_afternoon_stories_remain_within_target_cap(self):
        editions.publish({'articles': []}, 'morning', self.now)
        items = [
            {'id': f'new-{i}', 'title': f'Distinct afternoon development {i}',
             'url': f'https://source{i % 8}.example/story-{i}',
             'source': f'Source {i % 8}', 'category': 'world',
             'cluster_rep': True, 'score': 100-i}
            for i in range(30)
        ]
        afternoon = editions.publish({'articles': items}, 'afternoon', self.now)
        self.assertLessEqual(afternoon['article_count'], 15)
        self.assertEqual(30, afternoon['selection_report']['material_change']['new_stories'])


if __name__ == '__main__':
    unittest.main()
