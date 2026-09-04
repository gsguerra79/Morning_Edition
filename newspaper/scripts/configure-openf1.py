#!/usr/bin/env python3
"""Safely configure OpenF1 on the production host without terminal echo."""

import getpass
import os
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
KEYS = {"OPENF1_USERNAME", "OPENF1_PASSWORD"}


def dotenv_quote(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    username = getpass.getpass("OpenF1 username/email (hidden): ").strip()
    password = getpass.getpass("OpenF1 password (hidden): ")
    if not username or not password:
        raise SystemExit("Both values are required; nothing changed.")

    existing = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    kept = [line for line in existing
            if line.split("=", 1)[0].strip() not in KEYS]
    kept.extend([
        f"OPENF1_USERNAME={dotenv_quote(username)}",
        f"OPENF1_PASSWORD={dotenv_quote(password)}",
    ])
    temporary = ENV_FILE.with_suffix(".env.tmp")
    old_umask = os.umask(0o077)
    try:
        temporary.write_text("\n".join(kept) + "\n", encoding="utf-8")
        os.replace(temporary, ENV_FILE)
        os.chmod(ENV_FILE, 0o600)
    finally:
        os.umask(old_umask)
    print("OpenF1 credentials saved locally with mode 0600. Values were not displayed.")


if __name__ == "__main__":
    main()
