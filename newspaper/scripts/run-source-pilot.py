#!/usr/bin/env python3
import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source_pilot import run


def load(path, fallback=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return fallback


def atomic(path, value):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pilot-", suffix=".json", dir=os.path.dirname(path) or ".")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(value, fh, ensure_ascii=False, indent=2)
    os.replace(temporary, path)


parser = argparse.ArgumentParser()
parser.add_argument("--config", default="pilot-sources.sample.json")
parser.add_argument("--state", default="data/source-pilot.json")
args = parser.parse_args()
config = load(args.config)
if not isinstance(config, dict) or config.get("schema_version") != 1:
    raise SystemExit("invalid pilot configuration")
result = run(config, load(args.state, {}))
atomic(args.state, result)
print(json.dumps(result["summary"], ensure_ascii=False, indent=2, sort_keys=True))
