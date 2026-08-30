# The Forge Daily — First Prototype Execution Plan

## Document authority

This is the canonical execution record for turning the existing proof of
concept into the true first prototype of The Forge Daily. It governs scope,
step and phase status, acceptance gates, implementation decisions, problems,
evidence, and handoff between work sessions.

Update this document after every substantive execution session. Execute only
one owner-verifiable stage at a time. After implementing a stage, set it to
`Owner inspection` and present the ordinary browser-facing product surface.
Do not mark it closed or start the next stage until the owner explicitly agrees
it is closed. Record that agreement here before advancing. Tests, code, pull
requests, CI, logs, JSON, and shell commands are internal engineering evidence;
none can close a stage and the owner is never expected to review them.
Durable governing decisions may also be promoted to the workspace `MEMORY.md`;
detailed working state belongs here.

Last reconciled: 2026-08-30

## Delivery doctrine

Engineering gates protect production quality; they are not the product. A
safe, useful owner-facing slice must be delivered as soon as its own behavior
is verified, while longer observations and connector investigations continue
in the background. Internal pilots must never force the owner to wait for an
otherwise independent usable reader.

The owner must not be asked to operate the project through shell commands,
raw JSON, logs, or project directories. Those are operator evidence. Normal
use and progress visibility belong in the browser-facing product or in concise
proactive reports. If no suitable owner-facing surface exists, creating it is
unfinished product work and takes priority over further internal machinery.

This doctrine does not weaken stage closure, source-admission, archive
immutability, or safety gates. It changes sequencing *within* the active step:
deliver reversible usable capability first, then continue background evidence
collection. A usable slice does not silently close the active stage or unlock a
later stage.

## Owner-verifiable completion contract

This section supersedes the old numbered engineering steps and phase gates
later in this document. Those records remain as historical evidence only.

A stage can end only when all of the following are true:

1. The promised outcome is running in the private browser-facing reader.
2. Gabriel can inspect it through normal product controls without a terminal,
   raw API/JSON, logs, GitHub, or code review.
3. The interface clearly identifies what is live, incomplete, degraded, or
   excluded; hidden fallback behavior is a stage failure.
4. Gabriel explicitly says the visible outcome is accepted and the stage may
   close.

An implementation, passing test suite, merged pull request, shadow run, or
background pilot is never the end of a stage. These support delivery but do not
replace owner inspection.

If visual inspection exposes a defect, repair and republish the same stage.
Do not open the next stage, create a new research detour, or ask the owner to
inspect engineering artifacts.

## Complete source scope — authoritative from Stage 0

The live Notion `Clipping Sources` inventory was reconciled on 2026-08-30: 33
sources, seven owner pages, 27 active adapters, and six connector gaps. This is
the starting product scope. The eleven sources added on 2026-08-29 are merely a
subset of this inventory and must never again be described as the project scope.

- Brazil News (5): ((o))eco, Agência Brasil, Agência Pública, Globo,
  RioOnWatch.
- Comics (2): GiantITP, Wilde Life.
- Formula 1 (4): Formula 1, Motorsport, RaceFans, The Race.
- Ideas (5): Aeon, Medium, Psyche, Quanta Magazine, The Verge.
- Sports (5): ATP Tour, Alpinist, Climbing, ExplorersWeb, World Surf League.
- Technology & Things (10): Brickset, DPReview, Hackaday, New Atlas, PetaPixel,
  The Brothers Brick, The Gadgeteer, The Verge, Wired, Kickstarter.
- World News (3): BBC, Financial Times, Reuters.

Current connector gaps, visible rather than hidden: ATP Tour, Financial Times,
Kickstarter, Medium, Reuters, and World Surf League. The other 27 sources are
the initial live editorial corpus. Multi-page sources such as The Verge remain
one canonical source routed to each approved owner page.

## Rebaselined visual delivery stages

Status vocabulary: `Not started`, `In progress`, `Owner inspection`, `Closed`,
`Blocked`. Only Gabriel can move `Owner inspection` to `Closed`.

### Stage 0 — Source scope and reader truth

Status: In progress

Deliver in the reader:

- A browser-facing Source Coverage view showing all 33 Notion sources grouped
  under the seven owner pages.
- For every source: reading intent, Must include, Avoid, adapter state, and
  current ingestion health in plain language.
- The 27 active sources loaded into the running product from the compiled
  registry; the six connector gaps shown explicitly as incomplete.
- No legacy category names, hidden registry fallback, or eleven-source framing.

Owner inspection:

- Gabriel opens Source Coverage, sees all 33 sources and seven pages, and can
  compare the displayed intent with Notion without reviewing code.
- The reader visibly warns if its live registry or rule set is missing/stale.
- Close only when Gabriel accepts that the reader is working from the correct
  complete scope.

### Stage 1 — Editorial calibration and direct feedback

Status: Not started

Deliver in the reader:

- A live issue drawn from all currently active sources, grouped by the seven
  owner pages, with honest relevance thresholds and actual-issue diversity.
- A concrete “Why this is here” reason tied to owner intent; same-source copies
  are never called independent corroboration.
- “Not for me” on every card with short reason choices: wrong topic, low value,
  wrong source use, repetitive, promotional/filler, and do not show this story.
- Feedback immediately removes the card, persists across devices, and affects
  the next preview. A visible Feedback view lets Gabriel inspect and undo it.
- No quota filling: a short or empty page is preferable to poor material.

Owner inspection:

- Gabriel reads and rejects/keeps cards in the ordinary interface, refreshes,
  and sees the correction persist and influence the next issue.
- Close only when the visible source mix, topics, reasons, and rejection loop
  are credible enough to calibrate without developer intervention.

### Stage 2 — Complete all named source connectors

Status: Not started

Deliver in the reader:

- Working compliant connectors for ATP Tour, Financial Times, Kickstarter,
  Medium, Reuters, and World Surf League, using Gabriel's authorized access
  where applicable.
- Source Coverage changes each gap from incomplete to live only after its own
  sample cards are visible and attributable.
- Pilot/reliability evidence appears as a simple health indicator; it does not
  delay editorial corrections or require owner operation.

Owner inspection:

- Gabriel can open sample/current cards from every source and verify that each
  source is being used for the intended material.
- Close only after every source is visibly live or Gabriel explicitly accepts a
  displayed blocker or alternative.

### Stage 3 — Finite morning newspaper

Status: Not started

Deliver in the reader:

- The real 07:30 morning edition, immutable after publication, using the full
  live registry, accepted feedback, source rules, seven pages, grounded reasons,
  and bounded volume.
- Clear source provenance and honest empty/short sections.

Owner inspection:

- Gabriel reads an actual morning edition in the normal desktop and mobile
  interface and evaluates every page, source mix, story fit, and explanation.
- Close only when Gabriel accepts the visible morning product. A fixture or
  preview cannot close this stage.

### Stage 4 — Non-repetitive afternoon update

Status: Not started

Deliver in the reader:

- The real 16:30 update containing only genuinely new or materially changed
  stories, linked back to the morning where relevant.
- An explicit no-material-change state instead of filler.

Owner inspection:

- Gabriel compares an actual morning and afternoon pair in the reader and can
  see why each afternoon card qualifies.
- Close only after Gabriel accepts a real published pair.

### Stage 5 — Source-appropriate presentation

Status: Not started

Deliver in the reader:

- Comics as current panels with original-page links.
- Sports as schedules/results/status and relevant Brazilian competitors.
- Formula 1 with fact/analysis/rumor labeling and event/team/driver context.
- Kickstarter and development-stage gear with campaign, evidence, readiness,
  delivery-risk, support, and landed-cost context when available.
- Ordinary articles retain the accepted newspaper presentation.

Owner inspection:

- Gabriel inspects real examples of every presentation type in the reader.
- Close only when the formats are visibly useful and correctly differentiated.

### Stage 6 — Cross-device and operational acceptance

Status: Not started

Deliver in the reader:

- Read, saved, dismissed, feedback, and navigation state synchronized across
  desktop and mobile over LAN and Tailscale.
- Visible freshness and failure health, tested backup/recovery, and preserved
  historical editions.

Owner inspection:

- Gabriel performs the normal workflow on two devices and verifies state,
  editions, and recovery-visible behavior without technical tools.
- Close only when Gabriel accepts the complete first prototype.

## Mission

Produce a calm, finite, private morning newspaper and a non-repetitive
afternoon update from the owner's approved reading sources. The reader must
look like one publication, organize stories by the owner's topics, explain why
each story was selected, preserve immutable editions, synchronize reading
actions across devices, and keep FreshRSS and connector machinery behind the
curtain.

The first prototype is not complete merely because it fetches feeds and renders
cards. It is complete only when the edition demonstrates controlled source
coverage, owner-grounded editorial decisions, bounded volume, dependable
deduplication, source-specific presentation, and verified operation on desktop
and mobile over LAN and Tailscale.

## Source of truth hierarchy

1. The owner's live Notion `Clipping Sources` database defines requested
   sources, topic/page placement, reading intent, Must include, Avoid, and
   Sufficiency.
2. This execution plan defines delivery state, engineering decisions, evidence,
   risks, and unresolved questions.
3. `PRODUCT.md` defines the product contract.
4. `newspaper/SERVICE.md` defines commissioned runtime operations.
5. Code, generated configuration, connector state, and FreshRSS are
   implementation machinery. They must not silently override the first four.

The private Notion database and data-source identifiers belong in local
operator configuration, not this public repository.

## Baseline observed on 2026-08-29

- Running service: The Forge Daily on port 8090.
- Ingestion health: last run successful; 19 feeds; 333 retained articles.
- Latest morning edition: 321 articles.
- Latest afternoon update: 16 articles.
- Current pages: Technology & Gear, Photography, Outdoors & Mountaineering,
  Formula 1, World & Brazil, and Comics.
- Live Notion pages: Brazil News, World News, Formula 1, Technology & Things,
  Comics, Sports, and Ideas.
- Material baseline failure: a 321-item morning issue is not a calm, finite
  edition and fails the product contract.
- The current feed record supports only one category per source and cannot
  faithfully represent multi-page sources such as The Verge.
- Source-specific What I read, Must include, Avoid, and Sufficiency guidance is
  not yet enforced by the pipeline.
- Generic selection explanations state only that an item is timely for a
  category; they do not explain the owner's actual selection reason.
- Afternoon exclusion uses item IDs and the current cluster ID. It is vulnerable
  to changed headlines, URLs, and clusters between morning and afternoon.

## Approved governing decisions

- Notion remains the owner-facing source inventory. Engineering metadata must
  not be pushed into that intake view.
- A `TBD` row is a research queue described by Sufficiency, not a literal
  publication. Candidate sources are tested before the placeholder is replaced.
- The reader is organized by topic/page, never by source.
- FreshRSS remains ingestion plumbing and is not the normal reading interface.
- Morning editions publish at 07:30 America/Chicago.
- Afternoon updates publish at 16:30 America/Chicago and must not repeat
  unchanged morning stories.
- Published editions are immutable except for deliberate operator recovery.
- AI remains disabled until separately evaluated; the first prototype must be
  operationally sound without depending on an LLM.
- Source additions are controlled pilots, not bulk imports.
- Historical editions must survive prototype upgrades unchanged.
- Background source pilots do not block a bounded reader built from already
  approved production inputs.
- Owner-facing use and status are delivered through the reader and proactive
  plain-language reports, never through developer plumbing by default.

## Agreed replacements for the TBD source rows

All listed feeds returned parseable RSS on 2026-08-29. The owner approved them
as entries in the Notion source inventory on 2026-08-29. Adding a source to the
inventory does not automatically promote its feed into the live reader; live
ingestion remains a separately verified and reversible execution step.

### Innovative gear and high-tech gadgets

- New Atlas — unusual commercial technology, emerging products, materials,
  transportation, and hands-on reviews.
  Feed: `https://newatlas.com/index.rss`
- Hackaday — prototypes, experimental hardware, unconventional computers,
  fabrication, and credible development-stage projects.
  Feed: `https://hackaday.com/blog/feed/`
- Existing complement: The Gadgeteer for practical hands-on consumer reviews.

### LEGO news

- Brickset — releases, announcements, availability, set data, and reviews.
  Feed: `https://brickset.com/feed`
- The Brothers Brick — notable builds, design craft, advanced community work,
  and LEGO culture.
  Feed: `https://www.brothers-brick.com/feed/`
- Brick Fanatics is held in reserve because its working feed adds more rumor,
  franchise-entertainment, and promotional volume than the initial pilot needs.

### Thought pieces and ideas

- Aeon — long-form philosophy, science, society, history, and culture.
  Feed: `https://aeon.co/feed.rss`
- Quanta Magazine — deep explanatory mathematics, physics, biology, and
  computer science.
  Feed: `https://www.quantamagazine.org/feed/`
- Psyche — psychology, philosophy, and reflective practical pieces.
  Feed: `https://psyche.co/feed.rss`

### Broader Brazil coverage

- Agência Brasil — federal institutions, national developments, public policy,
  science, environment, and national sports.
  Feed: `https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml`
- Agência Pública — investigative reporting, accountability, social issues,
  and environmental coverage.
  Feed: `https://apublica.org/feed/`
- RioOnWatch — Rio communities, infrastructure, housing, environment, and
  public policy.
  Feed: `https://rioonwatch.org/?feed=rss2`
- ((o))eco — Brazilian environment, wildlife, conservation, and climate.
  Feed: `https://oeco.org.br/feed/`
- Globo remains the primary source for Flamengo and mainstream sports.

## Proposed first-prototype editorial defaults

These are implementation starting points to validate, not permanent editorial
law.

- Morning target: 30–45 story clusters overall.
- Afternoon target: no more than 10–15 material story clusters.
- A Must include story may exceed a section quota but must still be deduplicated.
- No ordinary high-volume source may consume more than 20 percent of an issue.
- Each populated page should normally receive at least one story and a bounded
  maximum appropriate to its priority and available material.
- Empty pages are omitted.
- Low-value rewrites, generic shopping lists, deal spam, gore, celebrity filler,
  shallow reaction pieces, and unchanged updates are excluded.
- When no material afternoon change exists, publish the explicit empty-update
  state rather than filler.

## Target architecture

### Editorial registry compiler

Build a read-only Notion importer that produces a validated local editorial
registry. The registry must preserve:

- source identity and canonical URL;
- zero, one, or multiple owner-selected topic/pages;
- What I read here;
- Must include;
- Avoid;
- Sufficiency/research-queue state;
- one or more resolved ingestion adapters or feeds held outside Notion;
- validation timestamp and last known ingestion health.

The compiler must reject malformed records, retain the last known-good registry
on Notion/API failure, emit a human-readable reconciliation report, and never
modify Notion during normal synchronization.

### Ingestion adapter boundary

Treat RSS as one adapter, not the entire architecture. Define a normalized item
contract for RSS and special connectors. Each item should carry stable source
identity, canonical URL, publication/update time, raw title/description,
candidate pages, provenance, and adapter-specific metadata.

Required connector investigations: Reuters, Financial Times, Medium,
Kickstarter, ATP Tour, and World Surf League. Do not evade blocked sources by
scraping against their terms or bypassing authentication/paywalls.

### Deterministic editorial engine

Before optional AI enrichment, implement auditable deterministic stages:

1. normalize URLs, text, dates, and source identity;
2. apply source-level Avoid and global safety/noise rules;
3. recognize Must include candidates;
4. route to one or more owner pages;
5. canonicalize stories and cluster corroborating coverage;
6. score recency, relevance, consequence, source intent, corroboration, and
   repetition penalties;
7. enforce source and section diversity caps;
8. select a bounded issue;
9. create a concrete selection explanation from matched rules;
10. freeze the immutable edition snapshot.

Every retained or rejected item should expose machine-readable reason codes for
debugging. The normal reader shows only concise human explanations.

### Stable story identity

Introduce a canonical story fingerprint independent of feed item ID and current
cluster membership. Persist morning fingerprints and material facts so the
afternoon engine can distinguish:

- unchanged rewrite — exclude;
- corroborating link with no material change — attach as provenance or exclude;
- meaningful development — include as an update linked to the morning cluster;
- genuinely new story — include normally.

### Special presentation adapters

- Comics: newest panel/image with a direct original-page link; no generic news
  summary card.
- Sports: event status, schedule/result, standings context, and relevant
  Brazilian competitors when available.
- Formula 1: label confirmed fact, analysis, rumor, or informed speculation;
  preserve team/driver/event context.
- Kickstarter/development-stage gear: campaign status, evidence, maker record,
  manufacturing readiness, delivery risk, support outlook, and landed-cost
  concerns when the source data supports them.
- Ordinary articles: publication-owned headline, concise summary, selection
  reason, time, primary provenance, and corroborating links.

## Historical engineering phases and gates — superseded

The records below document work previously performed and claims previously
made. They do not govern current execution and their `Closed` labels do not
mean the integrated product passed owner inspection. Current execution is
governed only by the rebaselined visual delivery stages above.

Status vocabulary for numbered steps: `Not started`, `In progress`, `Awaiting
owner closure`, `Closed`, `Blocked`.

Execution is strictly sequential. A later step may be planned but must not be
started until the immediately preceding step is `Closed` with the owner's
acceptance recorded in the progress ledger.

### Step 1 — Replace Notion TBD rows with agreed source entries

Status: Closed

Owner closure: accepted by Gabriel on 2026-08-29 after review of the
reconciliation evidence.

Work:

- Reuse each of the four TBD pages for the first agreed replacement in its
  queue, preserving the owner-selected Topic/Page.
- Create separate source rows for the remaining agreed replacements.
- Populate Source, URL, What I read here, Must include, and Avoid with concise
  source-specific guidance.
- Clear the obsolete queue statement from Sufficiency on the replaced rows.
- Query the complete table after mutation and verify that no TBD rows remain,
  all eleven agreed sources exist exactly once, and no unrelated owner rows
  changed.

Closure gate:

- Four original TBD pages have become agreed source records.
- Seven additional agreed source records exist.
- All eleven agreed records have the correct Topic/Page and usable guidance.
- No `TBD`, `TBD 2`, `TBD 3`, or `TBD 4` source remains.
- The owner reviews the reconciliation evidence and explicitly agrees Step 1 is
  closed.

### Step 2 — Preserve and instrument the baseline

Status: Closed

Owner closure: accepted by Gabriel on 2026-08-29 after GitHub recovery,
clean-clone restoration, and final `main` CI evidence.

This step executes Phase 0 below. It cannot start until Step 1 is closed.

Additional GitHub recovery work authorized 2026-08-29:

- Bootstrap the public `gsguerra79/Morning_Edition` repository from this
  project without exposing runtime state, owner-specific configuration,
  credentials, backups, Notion data, or private infrastructure details.
- Preserve the Cruxwire MIT license and attribution.
- Add CI and dependency/update governance appropriate to the repository.
- Push the structured project to `main`.
- Clone the repository into a clean temporary directory, run tests, validate
  Compose configuration, and prove that GitHub plus the separately verified
  runtime archive covers source and state recovery.

Additional closure gate:

- Public-repository privacy and secret preflight passes.
- CI passes on the pushed commit.
- Clean-clone tests and Compose validation pass.
- The recovery boundary between public source and private runtime state is
  documented.

### Step 3 — Build editorial registry and reconcile Notion

Status: Closed

Owner closure: accepted by Gabriel on 2026-08-29 after live reconciliation,
failure-preservation evidence, PR #6, and successful `main` CI.

This step executes Phase 1 below. It cannot start until Step 2 is closed.

### Step 4 — Implement bounded deterministic editorial selection

Status: Closed

Owner closure: accepted by Gabriel on 2026-08-29 after PR #7 merged and final
`main` CI passed.

This step executes Phase 2 below. It cannot start until Step 3 is closed.

### Step 5 — Harden clustering and afternoon material-change logic

Status: Closed

Owner closure: accepted by Gabriel on 2026-08-29 after PR #8 merged and final
`main` CI passed.

This step executes Phase 3 below. It cannot start until Step 4 is closed.

### Step 6 — Complete source adapters and run source pilots

Status: In progress

This step executes Phase 4 below. It cannot start until Step 5 is closed.

Delivery correction, ordered within Step 6:

1. Deliver a browser-facing bounded live preview from the current approved
   production digest. It must not rewrite today's immutable edition or any
   historical issue, and it must be verified over the owner's normal private
   network path. **Delivered and verified 2026-08-30.**
2. Use the live preview for immediate editorial calibration before expanding
   source volume. Repair relevance, diversity, routing, explanations, and
   owner feedback from actual visible failures; do not wait for the reliability
   pilot. **In progress.**
3. Keep the 72-hour eleven-source observation running independently in the
   background. Present its progress proactively in plain language; do not ask
   the owner to inspect files or run commands.
4. Continue compliant Medium, Financial Times, Reuters, ATP Tour, Kickstarter,
   and World Surf League adapter work without withholding the usable preview.
5. After pilot evidence matures, prepare deliberate promote/hold/reject
   recommendations. No source auto-promotes.

The bounded live preview is the immediate delivery target. Step 6 remains open
after that delivery until the source/adaptor exit gate is separately met and
the owner explicitly closes it.

Immediate editorial-repair acceptance criteria:

- The production preview loads the current compiled Notion editorial registry
  and private selection rules; missing rule assets are visible health failures,
  not silent generic fallback.
- Source dominance is measured against the issue actually shown, not the
  configured 40-story ceiling.
- Availability never fills a quota by itself: low-fit items may leave a page or
  issue intentionally short.
- Same-source duplicates are not called independent corroboration and do not
  receive a cross-source credibility boost.
- Globo/G1 is restricted to the owner's stated federal, country-scale, Rio de
  Janeiro, Flamengo, F1, environmental, wildlife, travel, and outdoors intent;
  regional TV-video indexes and unrelated state-local filler are excluded.
- Formula 1 marketing, entertainment, betting/markets, and driver-lifestyle
  filler do not displace news, results, schedules, rules, technical reporting,
  teams, and drivers.
- The reader offers a simple owner-facing “not for me” signal with a reason;
  feedback affects the next preview without requiring source removal, JSON, or
  terminal work.

### Step 7 — Align navigation and special presentations

Status: Not started

This step executes Phase 5 below. It cannot start until Step 6 is closed.

### Step 8 — Operational hardening and migration

Status: Not started

This step executes Phase 6 below. It cannot start until Step 7 is closed.

### Step 9 — Owner acceptance of the true first prototype

Status: Not started

This step executes Phase 7 below. It cannot start until Step 8 is closed.

### Phase 0 — Preserve and instrument the baseline

Status: Gate passed

Work:

- Back up current source configuration, runtime volume, state, and edition
  archive using a recoverable, timestamped procedure.
- Record exact container image/build, environment, settings, feed health, and
  current endpoint results.
- Add fixture-based tests for current edition immutability and state migration.
- Establish a shadow runtime or offline publication path that cannot overwrite
  production editions.

Exit gate:

- A tested restoration procedure exists.
- Historical editions compare byte-for-byte before and after a no-op rebuild.
- Shadow runs cannot write to production edition paths.

### Phase 1 — Editorial registry and Notion reconciliation

Status: Gate passed

Work:

- Define and test the editorial registry schema.
- Implement read-only import from Notion and local adapter mapping.
- Support multiple topic/pages per source.
- Detect new, changed, removed, TBD, and malformed rows.
- Generate a reconciliation report without changing Notion.

Exit gate:

- Every live Notion row is represented or explicitly reported.
- The eleven agreed replacements are imported from the reconciled owner table.
- A Notion outage leaves the last known-good registry and live edition intact.
- Multi-page sources route without duplicating the underlying item.

### Phase 2 — Bounded deterministic editorial selection

Status: Gate passed

Work:

- Separate candidate retention from issue selection.
- Add issue caps, page quotas, source-diversity limits, and Must include escape
  rules.
- Apply per-source reading, inclusion, and avoidance guidance.
- Produce auditable rejection and selection reason codes.
- Replace generic `why_selected` strings with grounded explanations.

Exit gate:

- A representative morning fixture produces 30–45 clusters.
- No normal source exceeds the configured dominance limit.
- All Must include and Avoid fixtures behave as specified.
- Re-running identical inputs produces identical selected issues.
- An empty or quiet input produces an honest finite result, not filler.

### Phase 3 — Stable clustering and afternoon material-change logic

Status: Gate passed

Work:

- Add normalized URL and stable story fingerprints.
- Persist morning story identity and material-fact signatures.
- Link corroboration and subsequent developments to a canonical story.
- Add fixtures for headline rewrites, URL changes, corrections, rumors becoming
  confirmed, and genuine material updates.

Exit gate:

- Unchanged morning stories cannot reappear under changed IDs or headlines.
- Material developments appear once and point back to the morning story.
- The afternoon update remains at or below its target cap.
- No-change afternoons publish the explicit no-material-change state.

### Phase 4 — Source completion and controlled source pilots

Status: In progress

Work:

- Ship the non-destructive bounded live preview before waiting for the pilot
  observation window.
- Add the eleven agreed inventory sources to shadow ingestion.
- Investigate compliant adapters for missing named sources.
- Observe at least 48–72 hours of candidate output.
- Measure relevance, rejection, overlap, volume, parsing failures, promotional
  leakage, and section contribution by source.
- Prepare a promote/hold/reject recommendation for each candidate.

Exit gate:

- The owner can use a finite browser-facing issue without waiting for the
  pilot window, and no historical edition is changed by that preview.
- Every named source has a working adapter, an explicit documented blocker, or
  an owner-approved alternative.
- Every new source has pilot evidence and a live-ingestion verdict.
- Live source promotion is a deliberate, reversible configuration change.

### Phase 5 — Owner-page navigation and special presentations

Status: Not started

Work:

- Align primary pages to Brazil News, World News, Formula 1, Technology &
  Things, Ideas, Sports, and Comics.
- Preserve photography and outdoors as useful subtopics or editorial groupings.
- Implement comic, sports, Formula 1, and development-stage gear cards.
- Ensure a source assigned to multiple pages is one story with appropriate
  placement, not duplicated reading work.

Exit gate:

- All seven owner pages render correctly when populated and disappear when
  empty.
- Wilde Life and Order of the Stick show the newest panel-oriented experience.
- Sports and Formula 1 fixtures show their required structured context.
- Desktop, tablet, and 390 px mobile layouts pass visual review.

### Phase 6 — Operational hardening and migration

Status: Not started

Work:

- Add health reporting per adapter, registry reconciliation, selection run, and
  publication.
- Add bounded retries, timeouts, last-known-good behavior, and failure alerts.
- Test restart, host reboot, unavailable Notion, unavailable source, malformed
  feed, partial connector failure, corrupt generated configuration, and full
  rollback.
- Document deployment, backup, restore, troubleshooting, and operator overrides.
- Run a shadow edition beside production and compare output before cutover.

Exit gate:

- The service survives every defined failure drill without corrupting editions.
- Production state and historical editions restore successfully from backup.
- LAN and Tailscale access work on phone and desktop.
- The scheduled morning and afternoon publications succeed for at least three
  consecutive days after cutover.

### Phase 7 — First prototype acceptance

Status: Not started

Acceptance requires the owner's review of real editions, not fixtures alone.

- Edition volume feels finite and readable.
- Topic/page organization matches the updated inventory.
- Selection reasons are useful and specific.
- Avoid rules suppress unwanted material without erasing wanted coverage.
- Must include rules reliably surface the promised coverage.
- Duplicate reporting is consolidated with clear provenance.
- Afternoon issues contain only new or materially changed stories.
- Comics and structured subjects render appropriately.
- Read, dismiss, save, history, mobile use, and cross-device synchronization
  behave correctly.
- Remaining shortcomings are explicitly recorded as post-prototype backlog.

Exit gate:

- Owner explicitly accepts the system as the true first prototype.

## Test strategy

- Unit tests: registry validation, rule matching, normalization, quotas, reason
  codes, story fingerprints, clustering, material-change classification, and
  special-card transformation.
- Contract tests: every adapter emits the same normalized item schema.
- Fixture tests: frozen representative RSS/Atom and connector responses so
  behavior is reproducible without live network dependence.
- Golden-edition tests: deterministic inputs produce reviewed immutable morning
  and afternoon JSON snapshots.
- Property/invariant tests: caps hold; rejected items never publish; published
  editions do not mutate; the afternoon cannot repeat an unchanged morning
  fingerprint.
- Integration tests: Notion-to-registry, adapters-to-candidates,
  candidates-to-edition, state actions, archive navigation, and recovery.
- Visual checks: desktop, tablet, and 390 px mobile screenshots for normal,
  empty, dense, error, and Previous Editions states.
- Operational drills: reboot, restart during refresh, missing network, one bad
  feed, Notion outage, disk/state corruption simulation, backup restoration,
  and rollback.

## Data migration and rollback doctrine

- Never mutate historical edition files during schema migration. Add readers or
  versioned migration views instead.
- Back up persistent volumes before every schema-changing deployment.
- Generate configuration atomically and retain the last known-good version.
- New registry, selection, and story-identity schemas carry explicit versions.
- Cutover occurs only after a shadow comparison and verified backup.
- Rollback restores the previous image/configuration while retaining compatible
  new evidence separately; do not destroy failed-run artifacts before diagnosis.
- Destructive cleanup requires explicit target verification and a recoverable
  path.

## Risks and mitigations

- Source volume overwhelms the reader — hard issue caps, page quotas, and
  source-dominance limits.
- Owner rules are ambiguous — report ambiguity; do not silently invent durable
  policy.
- Feed or site changes break ingestion — adapter health, fixtures, last-known-
  good configuration, and explicit degraded status.
- Paywalled or authenticated sources encourage brittle scraping — use compliant
  connectors or document the blocker.
- Deterministic rules miss semantic nuance — preserve evidence and reason codes;
  evaluate optional AI only after the non-AI baseline is trustworthy.
- Over-clustering merges distinct events — stable identity tests and visible
  corroborating provenance.
- Under-clustering repeats rewrites — fingerprint and material-change fixtures.
- Multi-page routing duplicates reading — canonical story identity with one
  reading state across placements.
- Source-affinity learning hides important material — apply affinity only after
  Must include and consequence gates; never allow it to suppress mandatory
  coverage.

## Open questions requiring owner decision

- Confirm whether Globo's Avoid text means: “avoid gory news, celebrity, and
  shallow topics.” Current wording says “Avoid gory news, focus on celebrity and
  shallow topics,” which is materially ambiguous.
- Approve or revise the proposed morning and afternoon size targets after the
  first shadow editions.
- Approve each TBD candidate after the 48–72 hour pilot evidence.
- Decide the durable save/archive destination after the first prototype proves
  the reading workflow.

## Decision register

Use IDs in code comments, commits, evidence notes, and problem records where
helpful.

| ID | Date | Status | Decision | Reason |
|---|---|---|---|---|
| FD-001 | 2026-08-24 | Accepted | Build The Forge Daily from the MIT-licensed Cruxwire foundation. | It best matched the required publication layout and reusable editorial mechanics. |
| FD-002 | 2026-08-24 | Accepted | Keep FreshRSS behind the reader as ingestion infrastructure. | Raw feed-reader presentation violates the coherent-publication contract. |
| FD-003 | 2026-08-24 | Accepted | Publish immutable morning and afternoon snapshots at 07:30 and 16:30 America/Chicago. | Finite issues and history are core product behavior. |
| FD-004 | 2026-08-24 | Accepted | Keep AI disabled until later evaluation. | The first prototype must remain understandable and operational without an LLM dependency. |
| FD-005 | 2026-08-29 | Accepted | Treat Notion TBD rows as research queues and test candidates before replacement. | The owner's rows must not be overwritten by unvalidated source guesses. |
| FD-006 | 2026-08-29 | Accepted | Replace the four current TBD queues with the eleven agreed source records listed above. | The feeds were live and collectively cover the stated gaps with complementary roles. Inventory approval is distinct from live-ingestion promotion. |
| FD-007 | 2026-08-29 | Accepted | Fix finite editorial selection before increasing live source volume. | The observed 321-item morning issue fails the product contract. |
| FD-008 | 2026-08-29 | Accepted | Maintain this file as canonical execution state and promote only durable facts to workspace memory. | Future sessions need continuity without bloating long-term memory with raw logs. |
| FD-009 | 2026-08-29 | Proposed default | Target 30–45 morning clusters and at most 10–15 afternoon clusters. | Provides a testable bounded starting point; owner review will calibrate it. |
| FD-010 | 2026-08-29 | Accepted | Execute numbered steps strictly one at a time; after verification, wait for explicit owner closure before marking a step closed or starting the next. | Prevents partial verification and plan drift from being mistaken for completed work. |
| FD-011 | 2026-08-29 | Accepted | Inventory approval and live-ingestion promotion are separate gates. | The owner table should express desired sources immediately, while production admission still requires verified adapter and editorial behavior. |
| FD-012 | 2026-08-29 | Accepted | Shadow execution uses a standalone Compose project, loopback-only port 18090, a dedicated shadow volume, shadow-only application paths, and disabled automatic publication deadlines. | Makes test publication mechanically unable to write production editions while keeping it easy to inspect. |
| FD-013 | 2026-08-29 | Accepted | Runtime backups pause the production container only during archive/checksum capture and are verified through restoration into a disposable Docker volume. | Produces a consistent snapshot and proves recoverability without overwriting production. |
| FD-014 | 2026-08-29 | Accepted | GitHub is canonical for public versioned code, tests, deployment definitions, sanitized examples, engineering documents, and execution history; private runtime backups remain a separate recovery layer. | A public repository must never contain reading state, editions, owner inventories, credentials, private endpoints, or operator evidence. |
| FD-015 | 2026-08-29 | Accepted | Changes reach `main` through pull requests with passing checks and container builds, even during initial bootstrap. | Makes repository recovery evidence reviewable and prevents an untested bootstrap from becoming the canonical source. |
| FD-016 | 2026-08-29 | Accepted | Notion reconciliation is read-only through the official CLI; a pure compiler merges private adapter mappings into an atomic, versioned local registry while a separate report records changes and faults. | Keeps owner intent separate from engineering plumbing, makes behavior testable without network access, and prevents API or validation failures from destroying the last known-good registry. |
| FD-017 | 2026-08-29 | Accepted | Adapter status describes technical availability (`active`, `planned`, or `blocked`) and does not itself promote a source into production editions. | Inventory reconciliation and live-ingestion admission remain separate controlled gates. |
| FD-018 | 2026-08-29 | Proposed default | Bound ordinary morning issues at 40 clusters, afternoon issues at 15, each ordinary source at 20 percent, and legacy pages at technology 8, photography 5, outdoors 5, F1 6, world 8, and comics 2. Must include matches may exceed these caps but remain deduplicated. | These values produce a 34-story representative morning fixture while preventing a high-volume source from filling the issue; owner review will calibrate them. |
| FD-019 | 2026-08-29 | Accepted | Compile owner guidance into a private, structured phrase-rule overlay and keep deterministic matching separate from the public registry/sample. | Source-specific Must include/Avoid behavior remains auditable without publishing the owner's detailed rule set or pretending deterministic substring matching has semantic judgment. |
| FD-020 | 2026-08-29 | Accepted | Store a compact identity/material-fact index for every morning candidate story, including candidates not printed in the bounded issue, and compare afternoon representatives against that frozen cutoff. | Prevents morning overflow or rewritten cluster members from masquerading as afternoon news while preserving the reader's finite morning issue. |
| FD-021 | 2026-08-29 | Accepted | Treat corrections, rumor-to-confirmed transitions, and newly introduced numeric facts as material developments; link them to the morning fingerprint. Treat matched rewrites without those signals as unchanged. | Provides explicit, testable first-prototype semantics without depending on an LLM or claiming semantic certainty the deterministic engine does not possess. |
| FD-022 | 2026-08-29 | Accepted | Observe candidate feeds every six hours for 72 hours in private ignored state; require at least 48 hours before any verdict and never auto-promote from pilot success. | Satisfies the evidence window with durable measurements while preserving the separate production-admission gate. |
| FD-023 | 2026-08-29 | Accepted | Treat owner-authenticated Medium preferences and FT subscription access as legitimate connector inputs; implement first-party HTML/API/email connectors for Reuters and WSL when RSS is absent. | The architecture explicitly defines RSS as one adapter, not the product boundary. A missing feed is an engineering routing problem, not grounds to reject an essential source. |
| FD-024 | 2026-08-30 | Accepted | Deliver safe owner-usable slices independently of long-running internal validation; background pilots may gate source promotion but may not block an already-verifiable bounded reader. Owner status/use surfaces must be browser-facing or proactively reported, not CLI/JSON instructions. | Gabriel correctly rejected waiting three days for a simple product and being told to follow its pilot from a project directory. Product delivery had been subordinated to engineering process. |
| FD-025 | 2026-08-30 | Accepted | Treat the Live Preview as the editorial calibration surface. Correct visible fit failures immediately from owner intent and feedback; reserve the 72-hour pilot for reliability and promotion evidence only. | The first live preview exposed severe editorial defects within minutes, proving that elapsed observation time is irrelevant to correcting selection quality. |
| FD-026 | 2026-08-30 | Accepted | Replace engineering-completion steps with owner-verifiable visual delivery stages. Tests, code review, CI, logs, APIs, and shell output cannot close a stage; only Gabriel's inspection of the running browser product and explicit acceptance can. | Gabriel will not perform code reviews and correctly requires inspectable outcomes before closure. |
| FD-027 | 2026-08-30 | Accepted | Treat all 33 current Notion Clipping Sources across all seven pages as the product scope from Stage 0. The eleven recent additions are a subset, not a pilot-sized substitute for the complete inventory. | The prior eleven-source framing materially misrepresented the intended product scope. |

## Problem and resolution log

Add entries when a defect, failed assumption, external limitation, or meaningful
tradeoff changes execution. Include evidence and the chosen resolution; do not
erase superseded conclusions.

| ID | Date | Phase | Problem/evidence | Resolution/status |
|---|---|---|---|---|
| FP-001 | 2026-08-29 | Baseline | Morning issue contained 321 articles while the product promises a calm finite edition. | Implementation resolved in Step 4: edition publication now selects a bounded set of cluster representatives. Production deployment remains intentionally pending owner closure. |
| FP-002 | 2026-08-29 | Baseline | Prototype categories do not match the seven live Notion Topic/Page options. | Open. Phase 1 imports owner pages; Phase 5 aligns navigation and presentation. |
| FP-003 | 2026-08-29 | Baseline | Feed configuration permits only one category per source. | Open. Phase 1 registry supports multiple topic/pages with one canonical reading item. |
| FP-004 | 2026-08-29 | Baseline | `why_selected` is generic and does not cite the owner rule that caused selection. | Implementation resolved in Step 4: reasons identify matched Must include guidance or cite the canonical source, owner reading intent, and page; the immutable edition also stores machine-readable selection/rejection evidence. Production deployment remains pending owner closure. |
| FP-015 | 2026-08-29 | Step 4 | The current 333-item live digest yielded only 60 cluster representatives across four populated legacy pages; page and source caps selected 15 rather than padding toward the 30-story morning target. | Correct honest behavior. The selector does not manufacture filler or weaken diversity caps. Phase 4 source pilots and Phase 5 page alignment will broaden qualified supply; the representative six-page fixture selects 34. |
| FP-005 | 2026-08-29 | Baseline | Afternoon exclusion can fail when a story's URL, headline, or cluster identity changes. | Resolved in Step 5 with normalized canonical URLs, content fingerprints, title-overlap fallback, a frozen morning candidate index, and explicit unchanged/material-update classification. |
| FP-016 | 2026-08-29 | Step 5 | The first shadow audit classified all 333 raw articles, so 176 non-representative cluster members appeared as material updates even though the selector correctly published none of them. | Resolved by applying material-change classification to the 60 story representatives, the same unit publication uses. The repeated identical-input shadow run reported 60 unchanged, zero material updates, zero new stories, and an explicit empty afternoon. |
| FP-017 | 2026-08-29 | Step 6 | The first seven-day pilot window returned zero Aeon and Psyche items even though both feeds were healthy; their latest posts were eight to nine days old. | Resolved for observation by using a declared 14-day pilot window. The clean restarted run parsed seven items from each. This does not silently alter production lookback policy. |
| FP-018 | 2026-08-29 | Step 6 | The existing Atom parser matched only bare `<entry>` tags, so Kickstarter's valid attributed `<entry xml:lang=...>` records parsed as zero. | Resolved with case-insensitive attributed RSS/Atom container matching and a regression fixture. Kickstarter still needs an editorial-scope verdict; its public feed is not automatically equivalent to the owner's requested technology-project coverage. |
| FP-019 | 2026-08-29 | Step 6 | Initial connector reporting framed absent public RSS for Reuters and WSL too close to a source failure and did not exploit the owner's authenticated Medium preferences or FT subscription. | Corrected by owner. Step 6 now requires source-specific connectors: Medium profile/following signals, Gabriel's FT subscription, and first-party non-RSS Reuters/WSL access. Only a demonstrated legal/technical impossibility after those paths are exhausted may be reported as blocked. |
| FP-020 | 2026-08-30 | Step 6 | Arc exposes both approved authenticated tabs over its native AppleScript inventory, but JavaScript content reads time out. The first connector draft incorrectly reported `ready` from tab presence alone. | Partially resolved: health now requires readable content, distinguishes missing from unreadable sources, and records timeout/command/JSON/empty-content failures. Current live result is two present tabs, zero readable sources, and `content_timeout` for both; no authenticated content has been ingested. Continue with a compliant content-read path without treating browser-relay pairing as a prerequisite. |
| FP-021 | 2026-08-30 | Step 6 delivery | The 72-hour source pilot was allowed to appear as a prerequisite for a usable reader, and the owner was given project-directory and `jq` commands as the way to follow it. After being told to correct this, implementation began before the canonical plan was amended. | Resolved for immediate delivery: governance was amended first, then the non-destructive bounded Live Preview was tested and commissioned over LAN and Tailscale. The pilot remains background evidence only. The broader doctrine remains binding for all future work. |
| FP-022 | 2026-08-30 | Step 6 editorial calibration | The first live preview selected 8 G1 cards, including regional TV-video indexes, plus low-value F1 marketing/lifestyle pieces. All deterministic base scores were tied at 6.0; G1 same-source clusters received the maximum cluster boost and were described as independent corroboration. The source cap allowed 8 because it used 20% of the 40-story ceiling rather than the 16-story issue. The running volume contained neither the compiled registry nor private rules, so explanations and filters silently fell back to generic behavior. | Open and immediate. Execute the editorial-repair criteria above before additional source expansion. Reliability observation continues independently and is not an excuse to defer visible quality corrections. |
| FP-023 | 2026-08-30 | Plan governance | Prior step closures were supported primarily by implementation, tests, shadow evidence, PRs, and CI, while critical integration remained invisible or absent in the running reader. The plan also allowed the eleven newly added sources to be mistaken for total scope despite 33 live Notion sources. | Superseded the old steps with Stages 0–6, each ending in a named browser-facing owner inspection. Reset active execution to Stage 0. All 33 sources and seven owner pages are authoritative from the first stage. Historical closed labels no longer imply product acceptance. |
| FP-006 | 2026-08-29 | Source review | Several requested named sources lack live ingestion: Reuters, Financial Times, Medium, Kickstarter, ATP Tour, and World Surf League. | Open and now machine-visible: Step 3 registry reconciliation reports exactly these six as planned connectors with no active adapter. Phase 4 investigates compliant adapters or records explicit blockers/alternatives. |
| FP-007 | 2026-08-29 | Source review | Globo Avoid guidance is linguistically ambiguous. | Waiting for owner confirmation; no durable filter should encode the ambiguous clause meanwhile. |
| FP-008 | 2026-08-29 | Step 1 | Four TBD queues needed to become eleven agreed source records without losing the owner-selected pages or disturbing unrelated rows. | Technically resolved: reused the four original pages, created seven companion pages, populated source-specific guidance, and reconciled the complete table. Awaiting owner closure. |
| FP-009 | 2026-08-29 | Step 2 | Initial backup invocation could resolve Docker's mount path but checked the root-owned directory as the ordinary user, then aborted before pausing or archiving. | Resolved by performing only the directory-existence check through non-interactive sudo. Removed the empty failed-attempt directory and completed a fresh backup. |
| FP-010 | 2026-08-29 | Step 2 | Initial shadow Compose launch inherited the production project name; after adding an explicit project name, the old disposable shadow container caused one name collision and the first health probe raced startup. | Resolved by verifying and removing only the disposable shadow container/volume, recreating under project `forge-daily-shadow`, and adding a bounded readiness poll. Production was never mounted or removed. |
| FP-011 | 2026-08-29 | Step 2 GitHub | The first local commit attempt failed because the workspace had no Git author identity. The branch push contained only the existing remote ancestry; no staged project files were published by that failed attempt. | Resolved with repository-local `Gabriel Guerra` / GitHub noreply attribution. Global Git configuration was not changed; the real bootstrap commit was then pushed and reviewed. |
| FP-012 | 2026-08-29 | Step 2 GitHub | The first public recovery verifier assumed the production image tag, while the clean-clone instructions built `morning-edition:recovery`. | Resolved in PR #2 by defaulting to the documented recovery tag and permitting an explicit `RESTORE_IMAGE` override. CI passed. |
| FP-013 | 2026-08-29 | Step 2 GitHub | The first clean-clone drill revealed that the archive checksum manifest stored the original absolute backup path. A copied backup could therefore validate the original archive rather than its own copy before restoration. | Resolved in PR #3: backup manifests now reference `runtime-data.tar` by basename and the verifier rejects non-portable targets. The backup manifest was regenerated and the entire clean-clone drill passed. |
| FP-014 | 2026-08-29 | Step 2 GitHub | The first successful `main` CI run warned that checkout v4 and setup-python v5 targeted deprecated Node 20 and were being forced onto Node 24. | Resolved by verifying the current official releases and upgrading both actions to v7 in PR #5. |

## Execution progress ledger

Append one row after each substantive work session. Evidence should name tests,
commands, screenshots, reports, or runtime observations sufficient for another
session to verify the claim.

| Date | Phase | Work completed | Evidence | Next action |
|---|---|---|---|---|
| 2026-08-29 | Planning | Read the complete live Notion inventory; resolved all four TBD queues into tested source candidates; inspected the running prototype, source/category configuration, edition logic, and live endpoints; established this hardened plan. | 14 candidate feeds fetched successfully; 11 agreed for the inventory; `/status` reported 19 feeds/333 retained articles; `/editions` reported a 321-item morning issue; source files and governing memory reviewed. | Execute Step 1, verify the reconciled Notion table, and wait for owner closure before Step 2. |
| 2026-08-29 | Step 1 | Replaced the four TBD pages in place with New Atlas, Brickset, Aeon, and Agência Brasil; created Hackaday, The Brothers Brick, Quanta Magazine, Psyche, Agência Pública, RioOnWatch, and ((o))eco; populated URLs and source-specific reading, inclusion, and avoidance guidance; cleared obsolete Sufficiency queue text. | Post-write full-table reconciliation returned 33 total rows, 0 TBD rows, 11 agreed rows, and 11 distinct agreed source names. The four reused pages retained Technology & Things, Technology & Things, Ideas, and Brazil News respectively; all seven new rows have the corresponding agreed page. | Await explicit owner confirmation that Step 1 is closed. Do not start Step 2. |
| 2026-08-29 | Step 1 closure | Gabriel explicitly accepted Step 1 as closed. Updated the canonical plan before advancing. | Owner message: “consider it closed and move on.” | Begin Step 2 only: baseline preservation and instrumentation. |
| 2026-08-29 | Step 2 | Added guarded runtime backup and disposable-volume restore verification scripts; recorded production identity and recovery procedure; added a standalone shadow Compose project; added byte-immutability and legacy-state regression tests; created and restored a production backup; ran shadow execution; performed a no-op production rebuild; reverified historical editions and service health. | A private ignored backup passed SHA-256 verification and restored into a disposable volume with all 12 edition checksums identical. Production editions remained byte-identical after shadow execution, rebuild, and the post-rebuild ingestion run. Six unit/regression tests passed. Final production status was successful with 19 feeds. Detailed host paths, image IDs, and runtime counts remain in the untracked operator evidence. | Await explicit owner confirmation that Step 2 is closed. Do not start Step 3. |
| 2026-08-29 | Step 2 extension | Gabriel withheld Step 2 closure until the project also had recoverable GitHub source management, then authorized execution against public repository `gsguerra79/Morning_Edition`. Reopened Step 2 while leaving Step 3 locked. | Repository preflight: public, `main`, initial README only, authenticated GitHub access over SSH, secret scanning and push protection enabled. | Bootstrap safely, push, verify CI, and prove clean-clone recovery before returning Step 2 for closure. |
| 2026-08-29 | Step 2 GitHub recovery | Initialized this project against `gsguerra79/Morning_Edition`; separated public source from ignored private runtime/operator material; moved CI to repository root; preserved the Cruxwire MIT license; added a repository overview, recovery boundary, sample-only image build, tests, Compose validation, container CI, and portable backup verification. Merged bootstrap PR #1 plus recovery fixes PR #2 and PR #3 after all checks passed. | Public preflight found no tracked backups, `.env`, live state, source OPML, live feed/category configuration, local runbooks, internal addresses, absolute operator paths, credentials, or private-key material. Final clean clone of `main` commit `84ae7a89cbe8b0ecc4360a2d7df2ff8ccdaeb488` passed six tests, both Compose validations, container build, copied-archive SHA-256 verification, and disposable-volume edition restoration. Temporary clones containing copied private backups were removed afterward. | Await explicit owner confirmation that Step 2 is closed. Do not start Step 3. |
| 2026-08-29 | Step 2 closure | Gabriel explicitly accepted Step 2 as closed after the final GitHub recovery and CI evidence. Updated the canonical plan before advancing. | Owner message: “closed - lets move.” | Begin Step 3 only: editorial registry and read-only Notion reconciliation. |
| 2026-08-29 | Step 3 | Added a pure editorial registry compiler, official-CLI read-only sync command with pagination, private adapter-map boundary, atomic last-known-good writes, explicit reconciliation reports, sample configuration, documentation, and five focused registry tests. Reconciled the complete live Notion source table. | Live reconciliation: 33 Notion rows → 33 registry sources; 27 sources with active adapters; six explicit planned connectors; zero missing adapter mappings; zero errors; all eleven formerly TBD replacements present. The Verge compiled once with both `Technology & Things` and `Ideas` and one adapter. A second identical sync reported 33 unchanged, wrote no registry, and retained SHA-256 `47b81d9e40d4c1f6da995fc81cc7a784959bc04762b8853f4299e401de3a7657`. A forced missing-CLI failure exited nonzero, reported `last_known_good_preserved: true`, and left that hash unchanged; the next live sync returned success. Eleven total unit/regression tests pass; private adapter and generated registry/report files are ignored. | Await explicit owner confirmation that Step 3 is closed. Do not start Step 4. |
| 2026-08-29 | Step 3 closure | Gabriel explicitly accepted Step 3 as closed after being shown the live and reviewable surfaces. Updated the canonical plan before advancing. | Owner message: “lets close it and move on.” | Begin Step 4 only: bounded deterministic editorial selection. |
| 2026-08-29 | Step 4 | Added and integrated deterministic issue selection with morning/afternoon caps, page quotas, canonical-source dominance limits, structured Must include/Avoid rules, grounded explanations, explicit rejection evidence, deterministic tie-breaking, cluster deduplication, and retained corroborating-source provenance. Added public sample rules, deployment wiring, operator documentation, and focused unit/integration tests. | Nineteen tests pass, including a 34-story representative six-page morning fixture, Must include/Avoid behavior, deterministic replay, honest empty input, publisher integration, and edition immutability. Compose validation, Python compilation, container build, diff checks, and the public-repository privacy boundary pass. An isolated shadow publication transformed the live 333-item digest into 60 candidate clusters and 15 selected stories across the four populated legacy pages, with all reasons present, 13 corroborated cards, and maximum source count 8/8. GitHub PR #7 opened and both checks passed. Production and historical editions were not modified. | Await explicit owner closure. Do not start Step 5. |
| 2026-08-29 | Step 4 closure | Gabriel explicitly accepted Step 4 as closed after PR #7 merged at `a29697e` and final `main` CI passed. Updated the canonical plan before advancing. | Owner message: “continue.” | Begin Step 5 only: stable story identity and afternoon material-change handling. |
| 2026-08-29 | Step 5 | Added versioned content fingerprints, canonical URL normalization, compact material-fact extraction, legacy compatibility, title-overlap matching, and deterministic new/unchanged/material-update classification. Morning editions persist a compact index for every candidate story; afternoon updates reject unchanged rewrites, link corrections/confirmations/new numeric facts to the morning fingerprint, and publish an explicit empty state when nothing changed. | All 32 tests pass, including headline/URL rewrites, corrections, rumor confirmation, new facts, genuinely new stories, stale morning overflow, explicit empty afternoons, target caps, malformed URLs, and edition immutability. Compilation, both Compose validations, container build, diff checks, and the public privacy boundary pass. On the repeated live 333-item digest, isolated shadow publication indexed 60 morning story representatives, printed 15, then classified all 60 as unchanged and published an explicit zero-story afternoon. Production edition checksums remained byte-identical. | Await explicit owner closure after GitHub PR and CI verification. Do not start Step 6. |
| 2026-08-29 | Step 5 closure | Gabriel explicitly accepted Step 5 as closed after PR #8 merged at `1560221` and final `main` CI passed. Updated the canonical plan before advancing. | Owner message: “continue.” | Begin Step 6 only: controlled source pilots and compliant adapter investigation. |
| 2026-08-29 | Step 6 initial observation | Added a public eleven-source pilot slate, durable private observation state, atomic runner, RSS/Atom compatibility fix, reliability/volume/promotion metrics, and tests. Installed a silent six-hour observer plus a one-shot 72-hour finalizer; neither can promote production feeds. Began official-source connector review. | Initial clean 14-day run: all 11 candidate feeds fetched and parsed; item counts ranged 5–60 except 10–40 for higher-volume sources; detected promotional ratios were zero for eight sources, 0.143 Hackaday, and 0.475 Brickset. Medium officially supports profile/publication/topic RSS. FT exposes a working international RSS feed but official republishing RSS terms also describe licensed keyed delivery. ATP publishes an official RSS page/endpoint but this host receives 403. Kickstarter exposes a public projects Atom feed after parser compatibility. Reuters and WSL have no verified compliant public adapter yet. | Continue six-hour observations through 72 hours; finish connector evidence and source-level relevance review; prepare explicit promote/hold/reject recommendations. Do not start Step 7. |
| 2026-08-30 | Step 6 authenticated-source continuation | Recovered the interrupted Arc connector work and bypassed the failed relay dependency with a read-only native Arc inventory over the already-authorized Mac Studio SSH path. Both intended tabs are discoverable. Hardened connector health so tab presence without page content cannot pass, and added explicit failure evidence. | Live inventory found `https://www.ft.com/` and Gabriel's Medium following-topic page. Both content executions timed out; connector now reports `partial`, two present sources, zero readable sources, and both sources unreadable. Four focused Arc tests pass. The source observer remains healthy with three durable six-hour samples; the 72-hour finalizer remains scheduled and production is unchanged. | Continue the independent Reuters/WSL and Medium/FT connector paths while the source-pilot observation window matures. Do not start Step 7 or promote sources. |
| 2026-08-30 | Step 6 delivery correction | Gabriel rejected the three-day wait and developer-plumbing status path, then required the canonical plan to adopt product-before-plumbing before further implementation. Added an explicit delivery doctrine, FD-024, FP-021, and ordered Step 6 so a non-destructive bounded browser preview ships before further connector work while the pilot continues independently. | Plan now distinguishes owner-usable delivery from source-promotion evidence and preserves all existing safety, immutability, and sequential closure gates. A live-preview code draft had been started prematurely; it remains uncommissioned and production remains unchanged pending verification under this amended plan. | Verify and deliver the bounded live preview first. Then continue background Step 6 connector and pilot work. Do not start Step 7. |
| 2026-08-30 | Step 6 usable delivery | Added a non-persistent bounded Live Preview as the first item in the existing browser Editions view, rebuilt the private service, and verified it through the normal LAN and Tailscale paths. The preview recomputes from the current digest and never writes the edition archive. | All 40 tests pass. Live ingestion completed successfully with 19 feeds and 362 retained articles. The preview produced 16 selected stories with grounded reasons. Both private-network routes served the UI and preview. Pre/post SHA-256 manifests for every historical edition were byte-identical. PR #10 passed both checks, merged at `9809115`, and the exact `main` merge commit passed final CI. | Resume background Step 6 connector and pilot work. Do not start Step 7. |
| 2026-08-30 | Step 6 first editorial audit | Audited every visible Live Preview card against the compiled Notion intent and selection evidence after Gabriel reported widespread mismatch. Reframed Step 6 so immediate editorial calibration precedes further source expansion while the reliability pilot remains background-only. | 16 visible cards: 8 G1, 4 Formula 1, 2 The Verge, and 2 Order of the Stick. G1 included six regional TV-video indexes; F1 included betting-market, career-list, and music-marketing filler. Every base score was 6.0. Source cap was 8; same-source clusters produced maximum boost and false corroboration language. Production lacked both registry and private rule files. | Implement and live-verify the immediate editorial-repair acceptance criteria. Do not wait for the pilot and do not start Step 7. |
| 2026-08-30 | Visual-stage rebaseline | Reconciled the live Notion inventory and replaced the engineering-step completion model with seven sequential owner-verifiable stages. Made ordinary browser inspection and Gabriel's explicit acceptance the only closure mechanism; code review is explicitly excluded from owner duties. Reset active work to Stage 0 Source scope and reader truth. | Live read-only reconciliation returned 33 unchanged sources, seven owner pages, 27 active adapters, six explicit connector gaps, zero errors, and no missing adapter mappings. The plan now names all 33 sources by page and defines the exact product surface Gabriel will inspect at every stage. | Implement Stage 0 only: browser Source Coverage, all 33 sources, seven pages, visible rules/health/gaps, and live registry/rule failure warnings. Present it for owner inspection; do not start Stage 1. |

## Session reconciliation checklist

At the start of substantive work:

1. Read this document and the latest relevant workspace memory.
2. Inspect current repository and runtime state; never assume the prior session's
   process is still healthy.
3. Identify the active numbered step and its unmet closure-gate clauses.
4. Preserve unrelated user changes.

Before ending substantive work:

1. Run verification proportional to the change.
2. Set the active step to `Awaiting owner closure` after evidence satisfies the
   technical gate. Set it to `Closed` only after explicit owner agreement.
3. Append the progress ledger.
4. Add or update problem and decision records.
5. Update `SERVICE.md` for commissioned operational changes.
6. Promote only durable governing facts to workspace memory.
7. State exactly what remains unverified or blocked.
