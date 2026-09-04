# Morning Edition

**Current release: v1.0.0 — The Forge Daily owner-accepted reader.**

Morning Edition is a private, self-hosted newspaper that turns approved reading
sources into a finite morning edition and a non-repetitive afternoon update.
It organizes stories by reader topic rather than publisher, consolidates
duplicate coverage, preserves provenance, and keeps immutable prior editions.

The reader is derived from the MIT-licensed
[Cruxwire](https://github.com/philoking/cruxwire) project. The upstream license
and copyright notice are preserved in [LICENSE](LICENSE).

## Repository layout

- `newspaper/` — the publication application, tests, container definition,
  shadow environment, and recovery tooling.
- `freshrss/` — optional FreshRSS ingestion deployment.
- `PRODUCT.md` — governing product contract.
- `CHANGELOG.md` — release history and the accepted v1 product boundary.
- `V2-ROADMAP.md` — reconciled, prioritized post-v1 product backlog.
- `EXECUTION-PLAN.md` — phased implementation, decisions, problems, gates, and
  verified progress.
- `EXISTING-SOLUTIONS.md` — alternatives and foundation evaluation.

## Quick verification

```sh
cd newspaper
python -m unittest -v
docker compose config --quiet
docker compose -f docker-compose.shadow.yaml config --quiet
docker build -t morning-edition:local .
```

## Configuration and privacy

Only sanitized sample configuration is versioned. Copy the examples to local
runtime configuration and keep the resulting files untracked. Never commit
credentials, live source inventories, reading state, saved items, immutable
edition archives, embeddings, internal addresses, or runtime backups.

GitHub recovers the application, tests, deployment definitions, and engineering
history. Production reader state and published editions require a separately
secured runtime backup; see
[the recovery boundary](newspaper/BASELINE-RECOVERY.md).
