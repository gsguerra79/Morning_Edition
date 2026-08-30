# Daily Clipping Service — FreshRSS engine

FreshRSS is deployed on the Forge Raspberry Pi as the synchronized feed and
reading-state engine. It is backend plumbing, not the owner-facing morning
edition. The product contract for the actual reading surface is in
`../PRODUCT.md`.

## Access boundary

Keep the service on a private network. Record LAN, overlay-network, and account
details only in an untracked operator runbook. Initial account creation is
completed in the FreshRSS browser setup so the operator selects the
administrator password.

## Runtime

- Image: `freshrss/freshrss:1.29.1` (pinned stable ARM64 image)
- Compose file on host: `/srv/freshrss/compose.yaml`
- Persistent application data and SQLite database: `/srv/freshrss/data`
- Extensions: `/srv/freshrss/extensions`
- Feed refresh: minutes 7 and 37 of every hour
- Restart policy: `unless-stopped`
- Port 8088 binds on the host's IPv4 interfaces. This avoids a Docker/Tailscale
  boot-order race while preserving the same private LAN and Tailscale endpoints;
  no router port-forward or public exposure is configured.

## Operations

```bash
cd /srv/freshrss
sudo docker compose ps
sudo docker compose logs --tail=100
sudo docker compose pull
sudo docker compose up -d
```

Back up `/srv/freshrss/data` and `/srv/freshrss/extensions`. A future phase will
add source inventory, classification, summarization, deduplication, and the
morning-edition presentation layer after FreshRSS is accepted as the engine.

## Source commissioning

The first owner-grounded feed set was commissioned on 2026-08-24. Historical
items from imported feeds were baselined as read after a FreshRSS database
backup, so only subsequently published items enter the live unread stream.

- OPML source inventories are intentionally untracked because they describe a
  specific reader's interests. Maintain them locally or generate them from the
  approved editorial registry.

Sources still requiring a non-native connector or a more precise definition:
Reuters, Financial Times, Medium, Kickstarter, ATP Tour, World Surf League, and
Do not substitute generic feeds merely to make a connector appear complete.
