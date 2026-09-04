import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

import pipeline


class NewsDeskTests(unittest.TestCase):
    def article(self, **changes):
        item = {
            'id': 'a1', 'title': 'National policy changes',
            'url': 'https://example.com/news/item', 'source': 'BBC World',
            'category': 'worldnews', 'score': 7.0, 'embedding': [1.0, 0.0],
        }
        item.update(changes)
        return item

    def test_world_and_us_source_contracts_are_distinct(self):
        self.assertTrue(pipeline.apply_news_desk_scope(self.article()))
        self.assertFalse(pipeline.apply_news_desk_scope(
            self.article(source='BBC US & Canada', category='worldnews')))
        self.assertTrue(pipeline.apply_news_desk_scope(
            self.article(source='BBC US & Canada', category='usnews')))
        self.assertFalse(pipeline.apply_news_desk_scope(
            self.article(source='Washington Post', category='worldnews')))

    def test_reuters_sitemap_routes_us_separately(self):
        now = datetime.now(timezone.utc)
        xml = f'''<urlset>
          <url><loc>https://www.reuters.com/world/us/congress-votes-2026-09-04/</loc>
            <news:publication_date>{now.isoformat()}</news:publication_date>
            <news:title>Congress votes</news:title></url>
          <url><loc>https://www.reuters.com/world/europe/election-2026-09-04/</loc>
            <news:publication_date>{now.isoformat()}</news:publication_date>
            <news:title>European election</news:title></url>
        </urlset>'''
        items = pipeline.parse_reuters_sitemap(
            xml, 'Reuters', 'worldnews', now - timedelta(hours=1))
        self.assertEqual(['usnews', 'worldnews'], [item['category'] for item in items])

    def test_cross_listed_domestic_and_canadian_items_are_routed_by_article(self):
        ft = self.article(source='Financial Times World', category='worldnews',
                          title='US economy adds 162,000 jobs')
        pipeline.route_news_article(ft)
        self.assertEqual(('usnews', 'Financial Times US'),
                         (ft['category'], ft['source']))
        canada = self.article(source='BBC US & Canada', category='usnews',
                              title='Canada announces new election rules')
        pipeline.route_news_article(canada)
        self.assertEqual(('worldnews', 'BBC World'),
                         (canada['category'], canada['source']))

    def test_news_page_does_not_fill_with_same_source_same_person(self):
        rows = []
        sources = ('BBC World', 'Financial Times World', 'Reuters', 'New York Times World')
        for i, source in enumerate(sources):
            rows.append(self.article(id=f'required-{i}', cluster_id=f'required-{i}',
                                     source=source, category='worldnews',
                                     title=f'{source} major headline', score=20-i,
                                     published_at='2026-09-04T12:00:00+00:00'))
        rows.extend([
            self.article(id='farage-1', cluster_id='farage-1', source='Financial Times World',
                         title='Nigel Farage faces financing questions', score=15,
                         published_at='2026-09-04T12:00:00+00:00'),
            self.article(id='farage-2', cluster_id='farage-2', source='Financial Times World',
                         title='Nigel Farage advisers leave conference', score=14,
                         published_at='2026-09-04T12:00:00+00:00'),
        ])
        selected, _ = pipeline.select_balanced_issue(rows)
        farage = [item for item in selected if 'Farage' in item['title']]
        self.assertEqual(1, len(farage))

    def test_unrelated_g1_state_portals_are_rejected_but_rio_is_kept(self):
        acre = self.article(source='Globo', category='brazilnews',
                            url='https://g1.globo.com/ac/acre/noticia/item.ghtml')
        rio = self.article(source='Globo', category='brazilnews',
                           url='https://g1.globo.com/rj/rio-de-janeiro/noticia/item.ghtml')
        self.assertFalse(pipeline.apply_news_desk_scope(acre))
        self.assertTrue(pipeline.apply_news_desk_scope(rio))

    def test_houston_routine_filler_is_rejected_but_civic_news_is_kept(self):
        food = self.article(source='Houston Chronicle', category='usnews',
                            title='The best new brunch spots',
                            url='https://www.houstonchronicle.com/food/restaurants/item.php')
        civic = self.article(source='Houston Chronicle', category='usnews',
                             title='Houston City Council approves Metro funding',
                             url='https://www.houstonchronicle.com/news/houston-texas/item.php')
        self.assertFalse(pipeline.apply_news_desk_scope(food))
        self.assertTrue(pipeline.apply_news_desk_scope(civic))

    def test_qualified_local_rejection_penalizes_same_scope_next_run(self):
        article = self.article(source='Globo', category='brazilnews',
                               url='https://g1.globo.com/sp/campinas-regiao/noticia/new.ghtml')
        feedback = {'feedback': [{
            'title': 'Routine Campinas bus-terminal update', 'source': 'Globo',
            'category': 'brazilnews', 'editorialScope': 'brazil_regional',
            'url': 'https://g1.globo.com/sp/campinas-regiao/noticia/old.ghtml',
            'reason': 'too_local',
        }]}
        with mock.patch.object(pipeline, '_load_user_state', return_value=feedback), \
             mock.patch.object(pipeline, '_embed_many', return_value=[[0.0, 1.0]]):
            pipeline.apply_feedback_learning([article], 'test-model')
        self.assertEqual('brazil_regional', article['editorial_scope'])
        self.assertEqual(4.0, article['feedback_penalty'])


if __name__ == '__main__':
    unittest.main()
