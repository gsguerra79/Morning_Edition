#!/usr/bin/env python3
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from source_pilot import run


ROOT = Path(__file__).resolve().parents[1]


def load(path, fallback=None):
    path = Path(path)
    try:
        if path.stat().st_size == 0:
            return fallback
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return fallback
    except json.JSONDecodeError as exc:
        backup = path.with_suffix(path.suffix + ".bak")
        try:
            with backup.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            raise SystemExit(f"invalid pilot state {path}: {exc}") from exc


def atomic(path, value):
    path = Path(path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pilot-", suffix=".json", dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(value, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        if path.exists():
            backup = path.with_suffix(path.suffix + ".bak")
            backup_fd, backup_tmp = tempfile.mkstemp(prefix=".pilot-backup-", suffix=".json", dir=path.parent)
            try:
                with os.fdopen(backup_fd, "wb") as out, path.open("rb") as source:
                    shutil.copyfileobj(source, out)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(backup_tmp, backup)
            except Exception:
                try:
                    os.unlink(backup_tmp)
                except FileNotFoundError:
                    pass
                raise
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "pilot-sources.sample.json"))
    parser.add_argument("--state", default=str(ROOT / "data/source-pilot.json"))
    args = parser.parse_args(argv)
    config = load(args.config)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise SystemExit("invalid pilot configuration")
    state_path = Path(args.state)
    lock_path = state_path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = run(config, load(state_path, {}))
        atomic(state_path, result)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
