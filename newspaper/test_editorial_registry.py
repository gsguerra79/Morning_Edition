import json
import os
import tempfile
import unittest

import editorial_registry as registry


def rich(value, kind="rich_text"):
    return {"type": kind, kind: [] if value is None else [{"plain_text": value}]}


def page(page_id, source, topics, **values):
    return {
        "id": page_id,
        "last_edited_time": values.get("edited", "2026-08-29T00:00:00.000Z"),
        "properties": {
            "Source": rich(source, "title"),
            "URL": {"type": "url", "url": values.get("url")},
            "Topic / Page": {"type": "multi_select", "multi_select": [
                {"name": topic} for topic in topics
            ]},
            "What I read here": rich(values.get("reads")),
            "Must include": rich(values.get("must")),
            "Avoid": rich(values.get("avoid")),
            "Sufficiency": rich(values.get("sufficiency")),
        },
    }


class EditorialRegistryTests(unittest.TestCase):
    def test_multi_page_source_has_one_adapter_and_multiple_topics(self):
        pages = [page("page-verge", "The Verge", ["Technology & Things", "Ideas"],
                      url="https://www.theverge.com/")]
        adapters = {"schema_version": 1, "sources": {"The Verge": [
            {"type": "rss", "status": "active",
             "url": "https://www.theverge.com/rss/index.xml"}
        ]}}
        compiled, report, fatal = registry.compile_registry(
            pages, adapters, generated_at="2026-08-29T00:00:00+00:00")
        self.assertFalse(fatal)
        self.assertEqual(1, len(compiled["sources"]))
        self.assertEqual(["Technology & Things", "Ideas"],
                         compiled["sources"][0]["topics"])
        self.assertEqual(1, len(compiled["sources"][0]["adapters"]))
        self.assertEqual(1, report["counts"]["active_sources"])

    def test_every_bad_row_is_represented_by_an_error(self):
        pages = [page("missing", "", ["Ideas"]),
                 page("one", "Same", ["Ideas"]),
                 page("two", "same", ["Ideas"])]
        adapters = {"schema_version": 1, "sources": {}}
        compiled, report, fatal = registry.compile_registry(pages, adapters)
        self.assertTrue(fatal)
        self.assertEqual(3, report["counts"]["notion_rows"])
        self.assertEqual(1, len(compiled["sources"]))
        self.assertEqual({"missing_source", "duplicate_source"},
                         {item["code"] for item in report["errors"]})

    def test_unchanged_reconciliation_does_not_rewrite_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = os.path.join(tmp, "registry.json")
            report_path = os.path.join(tmp, "report.json")
            pages = [page("one", "One", ["Ideas"])]
            adapters = {"schema_version": 1, "sources": {}}
            registry.reconcile_to_files(
                pages, adapters, registry_path, report_path,
                generated_at="2026-08-29T00:00:00+00:00")
            with open(registry_path, "rb") as handle:
                before = handle.read()
            _, report, fatal = registry.reconcile_to_files(
                pages, adapters, registry_path, report_path,
                generated_at="2026-08-30T00:00:00+00:00")
            self.assertFalse(fatal)
            self.assertFalse(report["registry_updated"])
            with open(registry_path, "rb") as handle:
                self.assertEqual(before, handle.read())

    def test_query_failure_preserves_last_known_good_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = os.path.join(tmp, "registry.json")
            report_path = os.path.join(tmp, "report.json")
            with open(registry_path, "w", encoding="utf-8") as handle:
                json.dump({"schema_version": 1, "generated_at": "old", "sources": []}, handle)
            with open(registry_path, "rb") as handle:
                before = handle.read()
            report = registry.write_failure_report(
                report_path, registry_path, "network unavailable",
                checked_at="2026-08-29T00:00:00+00:00")
            with open(registry_path, "rb") as handle:
                self.assertEqual(before, handle.read())
            self.assertTrue(report["last_known_good_preserved"])
            self.assertEqual("notion_query_failed", report["errors"][0]["code"])

    def test_adapter_change_is_reported(self):
        pages = [page("one", "One", ["Ideas"])]
        compiled, _, _ = registry.compile_registry(
            pages, {"schema_version": 1, "sources": {}})
        second = {"schema_version": 1, "sources": {"One": [
            {"type": "connector", "status": "planned", "connector": "one"}
        ]}}
        _, report, fatal = registry.compile_registry(pages, second, previous=compiled)
        self.assertFalse(fatal)
        self.assertEqual(["One"], report["changes"]["changed"])


if __name__ == "__main__":
    unittest.main()
