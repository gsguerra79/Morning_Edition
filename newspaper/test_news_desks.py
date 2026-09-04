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

    def test_agencia_brasil_sports_are_routed_out_of_brazil_news(self):
        sport = self.article(source='Agência Brasil', category='brazilnews',
                             title='Brasil conquista quatro medalhas',
                             url='https://agenciabrasil.ebc.com.br/esportes/noticia/2026-09/item')
        pipeline.route_news_article(sport)
        self.assertEqual('sports', sport['category'])

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

    def test_slow_brazil_specialists_receive_bounded_seven_day_window(self):
        self.assertEqual(168, pipeline._source_window_hours(
            'RioOnWatch', 'brazilnews', 24))
        self.assertEqual(168, pipeline._source_window_hours(
            'Agência Pública', 'brazilnews', 24))
        self.assertEqual(72, pipeline._source_window_hours(
            'Globo', 'brazilnews', 24))

    def test_brazil_issue_protects_sources_and_editorial_lanes(self):
        rows = [
            self.article(id='g1', cluster_id='g1', source='Globo',
                         category='brazilnews', title='Congresso debate política nacional', score=20),
            self.article(id='ab', cluster_id='ab', source='Agência Brasil',
                         category='brazilnews', title='Banco Central anuncia nova decisão', score=19),
            self.article(id='ap', cluster_id='ap', source='Agência Pública',
                         category='brazilnews', title='STF entra no centro das eleições', score=18),
            self.article(id='eco', cluster_id='eco', source='((o))eco',
                         category='brazilnews', title='Restauração avança na Amazônia', score=17),
            self.article(id='rio', cluster_id='rio', source='RioOnWatch',
                         category='brazilnews', title='Rio debate transporte metropolitano', score=16),
            self.article(id='exports', cluster_id='exports', source='Agência Brasil',
                         category='brazilnews', title='Exportação brasileira cresce em agosto', score=15),
            self.article(id='ap2', cluster_id='ap2', source='Agência Pública',
                         category='brazilnews', title='Congresso enfrenta nova investigação', score=14.9),
            self.article(id='ap3', cluster_id='ap3', source='Agência Pública',
                         category='brazilnews', title='Senado abre nova comissão nacional', score=14.8),
            self.article(id='eco2', cluster_id='eco2', source='((o))eco',
                         category='brazilnews', title='Mata Atlântica sofre com poluição', score=14.7),
            self.article(id='sports', cluster_id='sports', source='Agência Brasil',
                         category='brazilnews', title='Seleção vence torneio amistoso', score=14),
        ]
        selected, _ = pipeline.select_balanced_issue(rows)
        brazil = [item for item in selected if item['category'] == 'brazilnews']
        self.assertGreaterEqual(len(brazil), 6)
        self.assertEqual({'Globo', 'Agência Brasil', 'Agência Pública', '((o))eco', 'RioOnWatch'},
                         {item['source'] for item in brazil})
        self.assertNotIn('sports', {item['id'] for item in brazil})
        self.assertLessEqual(sum(item['source'] == 'Agência Pública' for item in brazil), 2)
        self.assertNotIn('ap3', {item['id'] for item in brazil})
        self.assertTrue({'national', 'rio', 'environment'} <=
                        {pipeline.brazil_story_lane(item) for item in brazil})

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
