# Morning Edition operations

Morning Edition is intended for private network deployment. Do not publish the
reader directly to the public Internet without adding appropriate
authentication, transport security, and an explicit threat review.

## Editorial behavior

- Morning and afternoon publication deadlines are configured in local time.
- Edition files are immutable unless an operator deliberately forces recovery.
- The home page groups stories by topic; sources appear as provenance.
- Deterministic summaries and title-token clustering work with AI disabled.
- **Home is a stable published paper.** It loads the immutable morning issue at
  07:30. After 16:30 it keeps every morning story and appends only new or
  materially changed afternoon stories, marked **Afternoon addition**. Browser
  refreshes do not reshuffle Home between those publication events.
- **Hot Metal** is separate from Home and reads the current ingest. Its strict
  gate admits only recent consequential world/Brazil headlines—catastrophes,
  major conflict or political developments, pivotal public addresses, and
  exceptional institutional events—from a major outlet or corroborated cluster.
  It is deliberately allowed to be empty rather than padded with ordinary news.
- If a saved category filter no longer exists, Home safely resets to All instead
  of appearing empty.
- Corpus admission preserves the best live story from each contributing source
  before filling remaining capacity under a per-source ceiling. Same-publisher
  clusters receive no corroboration boost. Durable pages use cadence-appropriate
  discovery and retention windows (for example, Ideas is not limited to the
  breaking-news window).
- The **Sources** view is the owner-facing source-of-truth surface. **Inventory**
  reconciles the imported editorial baseline with reader-managed feeds and
  shows reading intent, Must include, Avoid, coverage status, adapter state,
  fetch health, and connector gaps. **Manage sources** adds, validates, removes,
  restores, imports, and exports feeds. **Topics** edits section names, order,
  colors, and ranking intent. Editing canonical source guidance still requires
  the imported baseline until v2 makes those fields writable in the reader.
- The **Feedback** view records every **Not for me** decision with its selected
  reason. Feedback synchronizes through shared state, immediately removes the
  story cluster from Home, and can be undone in the browser.
- The **Weather** view uses the National Weather Service for Houston current,
  hourly, seven-day, and alert data; NOAA for Houston radar and Gulf/Atlantic
  storm reporting; and Open-Meteo for the compact Rio de Janeiro observation.
  Weather data is cached for 15 minutes in the production volume. If an
  upstream service is temporarily unavailable, the last successful payload is
  shown and marked cached rather than blanking the page.
- Financial Times and Reuters card images are delivered through a same-origin
  relay restricted to their approved image-CDN paths. Reuters story URLs and
  artwork come from Reuters' public first-party news sitemap rather than
  article-page scraping or a generic Google News placeholder.
- The Formula 1 topic opens with a structured race desk. Jolpica provides the
  current driver and constructor championships; Formula 1's public static timing
  archive provides the latest finalized race-weekend session classification,
  circuit weather and next-session time. When an OpenF1 supporter account is
  configured, the backend also adds a provisional current-session snapshot;
  credentials and bearer tokens never reach browser code. The payload is cached
  for five minutes and falls back to the last successful copy. The page carries
  twelve balanced stories; the All page intentionally carries its strongest six.
- Opening a story always records it in History. Whether opening also hides its
  Home card is a synced preference under **Settings → Display** and defaults to
  off; explicit Read Later and Not for me actions still retire cards.

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
- `/editions/today` — stable current front page (morning plus afternoon additions)
- `/hot-metal` — strictly selected consequential headlines from the current ingest
- `/source-coverage` — reader-ready source-scope and ingestion reconciliation
- `/weather` — cached Houston weather desk and Rio current observation
- `/f1` — cached championships and finalized race-weekend session results
- `/editions/YYYY-MM-DD-morning` — immutable issue
- `/editions/YYYY-MM-DD-afternoon` — immutable update
- `/feeds` and `/categories` — active source/topic configuration

Operator-specific endpoints, host paths, volume names, and backup evidence
belong in an untracked local runbook.
