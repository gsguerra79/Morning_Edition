# Morning Edition operations

Morning Edition is intended for private network deployment. Do not publish the
reader directly to the public Internet without adding appropriate
authentication, transport security, and an explicit threat review.

## Editorial behavior

- Morning and afternoon publication deadlines are configured in local time.
- Edition files are immutable unless an operator deliberately forces recovery.
- The home page groups stories by topic; sources appear as provenance.
- Deterministic summaries and title-token clustering work with AI disabled.

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
- `/editions/YYYY-MM-DD-morning` — immutable issue
- `/editions/YYYY-MM-DD-afternoon` — immutable update
- `/feeds` and `/categories` — active source/topic configuration

Operator-specific endpoints, host paths, volume names, and backup evidence
belong in an untracked local runbook.
