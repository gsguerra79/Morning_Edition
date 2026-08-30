#!/usr/bin/env python3
"""Read approved authenticated sources from existing Arc tabs."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arc_connector import health, read_tabs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="mac-studio",
                        help="Operator-defined SSH host alias for the Mac running Arc")
    parser.add_argument("--include-text", action="store_true")
    args = parser.parse_args()
    tabs = read_tabs(args.host)
    result = {
        "health": health(tabs),
        "tabs": [
            {
                "source": tab.source,
                "title": tab.title,
                "url": tab.url,
                "text": tab.text if args.include_text else None,
                "text_length": len(tab.text),
                "content_error": tab.content_error,
            }
            for tab in tabs
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["health"]["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
