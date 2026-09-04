import tempfile
import unittest
from pathlib import Path
from unittest import mock

import live_desks


def article(item_id, category='formula1', kind='news', source='Source', published='2026-09-04T12:00:00Z'):
    return {
        'id': item_id, 'category': category, 'f1_kind': kind,
        'source': source, 'published_at': published, 'title': item_id,
        'url': f'https://example.com/{item_id}', 'score': 10,
    }


class LiveDeskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'live-desks.json')

    def tearDown(self):
        self.tmp.cleanup()

    def test_home_f1_ids_are_subset_of_same_full_desk(self):
        items = [
            article('r1', kind='results_updates', source='Autosport'),
            article('r2', kind='results_updates', source='Motorsport'),
            article('t1', kind='technical', source='The Race'),
            article('p1', kind='preview_forecast', source='Formula1.com'),
            article('n1', kind='news', source='RaceFans'),
            article('n2', kind='news', source='Autosport'),
            article('x1', kind='rumor_interview', source='Motorsport'),
        ]
        result = live_desks.build({'generated_at': 'one', 'articles': items}, self.path)
        desk = result['desks']['formula1']
        self.assertEqual(6, len(desk['front_page_ids']))
        self.assertTrue(set(desk['front_page_ids']).issubset({a['id'] for a in desk['articles']}))

    def test_normal_f1_refresh_replaces_at_most_two_retained_cards(self):
        first = [article(f'n{i}', kind='news', source=f'S{i}') for i in range(8)]
        before = live_desks.build({'generated_at': 'one', 'articles': first}, self.path)
        second = [article(f'new{i}', kind='technical', source=f'N{i}') for i in range(6)] + first
        after = live_desks.build({'generated_at': 'two', 'articles': second}, self.path)
        old_ids = set(before['desks']['formula1']['front_page_ids'])
        new_ids = set(after['desks']['formula1']['front_page_ids'])
        self.assertLessEqual(len(new_ids - old_ids), 2)

    def test_new_result_updates_bypass_normal_churn_cap(self):
        first = [article(f'n{i}', kind='news', source=f'S{i}') for i in range(8)]
        before = live_desks.build({'generated_at': 'one', 'articles': first}, self.path)
        results = [article(f'r{i}', kind='results_updates', source=f'R{i}') for i in range(3)]
        after = live_desks.build({'generated_at': 'two', 'articles': results + first}, self.path)
        old_ids = set(before['desks']['formula1']['front_page_ids'])
        new_ids = set(after['desks']['formula1']['front_page_ids'])
        self.assertGreaterEqual(len(new_ids - old_ids), 3)

    def test_home_f1_prefers_race_desk_over_paddock_material(self):
        desk = [
            article('fp2', kind='results_updates', source='Autosport'),
            dict(article('engine', kind='technical', source='Motorsport'),
                 title='Honda introduces new engine upgrade'),
            dict(article('incident', kind='news', source='RaceFans'),
                 title='Stroll faces investigation after FP2 incident'),
            dict(article('strategy', kind='news', source='The Race'),
                 title='Ferrari long run strategy and tyre degradation'),
            dict(article('qualifying', kind='news', source='Formula1.com'),
                 title='Italian GP qualifying preview'),
            dict(article('penalty', kind='news', source='BBC'),
                 title='Driver receives grid penalty'),
        ]
        paddock = [
            dict(article('prediction', kind='preview_forecast'),
                 title='Montoya predicts a lot of drama'),
            dict(article('future', kind='news'), title='F1 races shortened in 2027'),
            dict(article('colour', kind='rumor_interview'), title='Why Ferrari races in red'),
        ]
        result = live_desks.build({'generated_at': 'one', 'articles': paddock + desk}, self.path)
        self.assertEqual({a['id'] for a in desk},
                         set(result['desks']['formula1']['front_page_ids']))

    def test_comics_always_returns_latest_installment_per_series(self):
        comics = [
            article('g-old', 'comics', source='The Order of the Stick', published='2026-09-01'),
            article('g-new', 'comics', source='The Order of the Stick', published='2026-09-04'),
            article('w-old', 'comics', source='Wilde Life', published='2026-09-02'),
            article('w-new', 'comics', source='Wilde Life', published='2026-09-03'),
        ]
        result = live_desks.build({'generated_at': 'one', 'articles': comics}, self.path)
        self.assertEqual(['g-new', 'w-new'], result['desks']['comics']['front_page_ids'])

    def test_comic_subscriptions_bypass_stale_issue_ranking(self):
        giant_feed = '<rss><channel><item><title>1348: Fading Odds</title><link>http://www.giantitp.com/comics/oots1348.html</link></item></channel></rss>'
        wilde_feed = '<rss><channel><item><title>Wilde Life - 1642</title><link>https://www.wildelifecomic.com/comic/1642</link><pubDate>Fri, 04 Sep 2026 04:55:43 -0400</pubDate><description>&lt;img src="https://www.wildelifecomic.com/comicsthumbs/1642.png"&gt;</description></item></channel></rss>'
        pages = {
            'https://www.giantitp.com/comics/oots.rss': giant_feed,
            'http://www.giantitp.com/comics/oots1348.html': '<img src="https://i.giantitp.com/comics/oots/oots1348.png">',
            'https://www.wildelifecomic.com/comic/rss': wilde_feed,
            'https://www.wildelifecomic.com/comic/1642': '<img id="cc-comic" src="/comics/1642.png">',
        }
        stale = [
            article('g-old', 'comics', source='GiantITP', published='2026-08-01'),
            article('w-old', 'comics', source='Wilde Life', published='2026-08-01'),
        ]
        with mock.patch.object(live_desks, '_fetch', side_effect=lambda url, timeout=10: pages[url]):
            result = live_desks.build({'generated_at': 'one', 'articles': stale}, self.path,
                                      fetch_current_comics=True)
        comics = result['desks']['comics']['articles']
        self.assertEqual(['1348: Fading Odds', 'Wilde Life - 1642'], [a['title'] for a in comics])
        self.assertTrue(all(a.get('image') for a in comics))

    def test_current_comic_survives_full_artwork_timeout(self):
        feed = '<rss><channel><item><title>Wilde Life - 1642</title><link>https://www.wildelifecomic.com/comic/1642</link><description>&lt;img src="https://www.wildelifecomic.com/comicsthumbs/1642.png"&gt;</description></item></channel></rss>'
        def fetch(url, timeout=10):
            if url.endswith('/comic/rss'):
                return feed
            raise TimeoutError('page image timed out')
        with mock.patch.object(live_desks, 'COMIC_FEEDS', (('Wilde Life', 'https://www.wildelifecomic.com/comic/rss'),)), \
             mock.patch.object(live_desks, '_fetch', side_effect=fetch):
            comics = live_desks._fetch_current_comics([], 'now')
        self.assertEqual('Wilde Life - 1642', comics[0]['title'])
        self.assertIn('/comicsthumbs/1642.png', comics[0]['image'])


if __name__ == '__main__':
    unittest.main()
