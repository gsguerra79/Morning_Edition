import unittest

import arc_connector


class ArcConnectorTests(unittest.TestCase):
    def test_reads_only_allowed_first_party_tabs(self):
        inventory = "\n".join([
            'm1|||Following|||https://medium.com/me/following-feed/topics/neuroscience',
            'f1|||Home|||https://www.ft.com/',
            'x1|||Private|||https://example.com/',
        ])
        content = {
            "m1": '{"title":"Following","url":"https://medium.com/me/following-feed/topics/neuroscience","text":"Topics"}',
            "f1": '{"title":"Home","url":"https://www.ft.com/","text":"Financial Times"}',
        }
        def runner(_host, script, _timeout=10):
            if "set rows" in script:
                return inventory
            return next((value for key, value in content.items() if key in script), "")
        tabs = arc_connector.read_tabs("unused", runner)
        self.assertEqual(["medium", "financial-times"], [tab.source for tab in tabs])
        self.assertEqual("ready", arc_connector.health(tabs)["status"])

    def test_missing_source_is_partial(self):
        inventory = 'm1|||Following|||https://medium.com/me/following'
        tabs = arc_connector.read_tabs(
            "unused", lambda _host, script, _timeout=10:
            inventory if "set rows" in script else "")
        result = arc_connector.health(tabs)
        self.assertEqual("partial", result["status"])
        self.assertEqual(["financial-times"], result["missing"])

    def test_present_but_unreadable_sources_are_not_ready(self):
        inventory = "\n".join([
            'm1|||Following|||https://medium.com/me/following',
            'f1|||Home|||https://www.ft.com/',
        ])
        tabs = arc_connector.read_tabs(
            "unused", lambda _host, script, _timeout=10:
            inventory if "set rows" in script else "")
        result = arc_connector.health(tabs)
        self.assertEqual("partial", result["status"])
        self.assertEqual(["financial-times", "medium"], result["unreadable"])
        self.assertTrue(all(tab.content_error == "empty_content" for tab in tabs))

    def test_script_has_no_navigation_or_tab_creation(self):
        script = (arc_connector._inventory_script() +
                  arc_connector._content_script("safe-id")).lower()
        for forbidden in ("make new tab", "set url", "reload", "select t", "click"):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
