import unittest
from datetime import datetime, timedelta, timezone

import pressing_news


class HotMetalTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 4, 16, 0, tzinfo=timezone.utc)

    def story(self, **overrides):
        story = {
            'id': 'a', 'cluster_id': 'a', 'cluster_rep': True,
            'title': 'Government declares state of emergency after earthquake',
            'summary': 'Evacuations are underway.', 'source': 'Reuters',
            'category': 'worldnews', 'score': 9,
            'published_at': (self.now - timedelta(hours=1)).isoformat(),
        }
        story.update(overrides)
        return story

    def test_admits_recent_consequential_major_source_headline(self):
        result = pressing_news.select({'generated_at': self.now.isoformat(),
                                      'articles': [self.story()]}, self.now)
        self.assertEqual('hot-metal', result['id'])
        self.assertEqual(1, result['article_count'])
        self.assertEqual('Catastrophe or public emergency',
                         result['articles'][0]['hot_metal_reason'])

    def test_rejects_generic_recent_news_and_sports(self):
        result = pressing_news.select({'articles': [
            self.story(id='generic', cluster_id='generic', title='Minister discusses new policy'),
            self.story(id='sport', cluster_id='sport', category='sports',
                       title='Earthquake win shakes up tennis draw'),
        ]}, self.now)
        self.assertEqual(0, result['article_count'])

    def test_rejects_old_or_unconfirmed_minor_source_item(self):
        result = pressing_news.select({'articles': [
            self.story(id='old', cluster_id='old',
                       published_at=(self.now - timedelta(hours=19)).isoformat()),
            self.story(id='minor', cluster_id='minor', source='Local Blog'),
        ]}, self.now)
        self.assertEqual(0, result['article_count'])

    def test_non_major_source_requires_corroboration(self):
        result = pressing_news.select({'articles': [
            self.story(source='Regional News', cluster_size=2),
        ]}, self.now)
        self.assertEqual(1, result['article_count'])

    def test_output_is_bounded(self):
        stories = [self.story(id=f'a{i}', cluster_id=f'a{i}', score=20-i)
                   for i in range(15)]
        result = pressing_news.select({'articles': stories}, self.now)
        self.assertEqual(pressing_news.MAX_ITEMS, result['article_count'])
