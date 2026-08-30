#!/usr/bin/env python3
"""Read Notion through the official CLI and reconcile a local registry."""

import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from editorial_registry import load_json, reconcile_to_files, write_failure_report  # noqa: E402


def query_all(data_source_id, ntn="ntn", page_size=100):
    pages, cursor = [], None
    while True:
        command = [ntn, "datasources", "query", data_source_id,
                   "--limit", str(page_size), "--json"]
        if cursor:
            command.extend(["--start-cursor", cursor])
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        payload = json.loads(completed.stdout)
        results = payload.get("results")
        if not isinstance(results, list):
            raise ValueError("Notion query did not return results[]")
        pages.extend(results)
        if not payload.get("has_more"):
            return pages
        cursor = payload.get("next_cursor")
        if not cursor:
            raise ValueError("Notion query reported has_more without next_cursor")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-source", default=os.environ.get("NOTION_DATA_SOURCE_ID"),
                        help="Notion data source ID; may use NOTION_DATA_SOURCE_ID")
    parser.add_argument("--adapters", required=True, help="Private adapter mapping JSON")
    parser.add_argument("--registry", required=True,
                        help="Last-known-good generated registry JSON")
    parser.add_argument("--report", required=True,
                        help="Generated reconciliation report JSON")
    parser.add_argument("--ntn", default="ntn", help="Official Notion CLI executable")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.data_source:
        print("--data-source or NOTION_DATA_SOURCE_ID is required", file=sys.stderr)
        return 2
    try:
        adapters = load_json(args.adapters)
        if adapters is None:
            raise ValueError(f"adapter mapping not found: {args.adapters}")
        pages = query_all(args.data_source, ntn=args.ntn)
        _, report, fatal = reconcile_to_files(
            pages, adapters, args.registry, args.report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if fatal else 0
    except Exception as exc:
        report = write_failure_report(args.report, args.registry, exc)
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
