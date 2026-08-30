#!/usr/bin/env python3
"""Compile the private editorial registry into runtime feed/category files."""

import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source_coverage import runtime_scope


def atomic(path, value):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".scope-", suffix=".json",
                                     dir=os.path.dirname(path) or ".")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(value, fh, ensure_ascii=False, indent=2)
    os.replace(temporary, path)


parser = argparse.ArgumentParser()
parser.add_argument("--registry", required=True)
parser.add_argument("--feeds", required=True)
parser.add_argument("--categories", required=True)
args = parser.parse_args()
with open(args.registry, encoding="utf-8") as fh:
    registry = json.load(fh)
categories, feeds = runtime_scope(registry)
atomic(args.feeds, feeds)
atomic(args.categories, categories)
print(json.dumps({"sources": len({feed['source'] for feed in feeds}),
                  "feeds": len(feeds), "categories": len(categories)}))
