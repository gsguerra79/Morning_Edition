# Morning Edition operations

Morning Edition is intended for private network deployment. Do not publish the
reader directly to the public Internet without adding appropriate
authentication, transport security, and an explicit threat review.

## Editorial behavior

- Morning and afternoon publication deadlines are configured in local time.
- Edition files are immutable unless an operator deliberately forces recovery.
- The home page groups stories by topic; sources appear as provenance.
- Deterministic summaries and title-token clustering work with AI disabled.
- The Editions view begins with a bounded **Live Preview** built from the
  current digest. It updates after ingestion and never writes or replaces an
  immutable edition file.
- Home reads that finite selected preview rather than exposing the raw retained
  ingestion pool. If a saved category filter no longer exists, Home safely
  resets to All instead of appearing empty.
- The **Sources** view is the owner-facing reconciliation surface for the live
  Notion editorial registry. It groups the complete inventory by owner page and
  shows reading intent, Must include, Avoid, adapter state, production loading,
  per-source fetch health, connector gaps, and missing rule assets.
- The **Feedback** view records every **Not for me** decision with its selected
  reason. Feedback synchronizes through shared state, immediately removes the
  story cluster from Home, and can be undone in the browser.

## Operations

```sh
cd newspaper
sudo docker compose ps
sudo docker compose logs --tail 100
sudo docker compose up -d --build
curl -X POST http://127.0.0.1:8090/refresh
```

Persistent state, saved items, digest data, and immutable editions live in the
Compose-managed production volume. Sample feeds and categories seed only a new
volume; later in-app changes survive image rebuilds.

## API checks

- `/status` — ingestion health
- `/editions` — archive index
- `/editions/live-preview` — non-persistent bounded issue from the current digest
- `/source-coverage` — reader-ready source-scope and ingestion reconciliation
- `/editions/YYYY-MM-DD-morning` — immutable issue
- `/editions/YYYY-MM-DD-afternoon` — immutable update
- `/feeds` and `/categories` — active source/topic configuration

Operator-specific endpoints, host paths, volume names, and backup evidence
belong in an untracked local runbook.
