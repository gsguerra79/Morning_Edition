# The Forge Daily — First Prototype Execution Plan

## Document authority

This is the canonical execution record for turning the existing proof of
concept into the true first prototype of The Forge Daily. It governs scope,
step and phase status, acceptance gates, implementation decisions, problems,
evidence, and handoff between work sessions.

Update this document after every substantive execution session. Execute only
one numbered step at a time. After implementing and verifying a step, set it to
`Awaiting owner closure` and present the evidence. Do not mark it closed or
start the next step until the owner explicitly agrees it is closed. Record that
agreement here before advancing. Do not mark a phase complete from code
presence alone: record the verification evidence that passed its exit gate.
Durable governing decisions may also be promoted to the workspace `MEMORY.md`;
detailed working state belongs here.

Last reconciled: 2026-08-29

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

## Execution phases and gates

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

Status: Awaiting owner closure

This step executes Phase 1 below. It cannot start until Step 2 is closed.

### Step 4 — Implement bounded deterministic editorial selection

Status: Not started

This step executes Phase 2 below. It cannot start until Step 3 is closed.

### Step 5 — Harden clustering and afternoon material-change logic

Status: Not started

This step executes Phase 3 below. It cannot start until Step 4 is closed.

### Step 6 — Complete source adapters and run source pilots

Status: Not started

This step executes Phase 4 below. It cannot start until Step 5 is closed.

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

Status: Awaiting owner closure

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

Status: Not started

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

Status: Not started

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

Status: Not started

Work:

- Add the eleven agreed inventory sources to shadow ingestion.
- Investigate compliant adapters for missing named sources.
- Observe at least 48–72 hours of candidate output.
- Measure relevance, rejection, overlap, volume, parsing failures, promotional
  leakage, and section contribution by source.
- Prepare a promote/hold/reject recommendation for each candidate.

Exit gate:

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

## Problem and resolution log

Add entries when a defect, failed assumption, external limitation, or meaningful
tradeoff changes execution. Include evidence and the chosen resolution; do not
erase superseded conclusions.

| ID | Date | Phase | Problem/evidence | Resolution/status |
|---|---|---|---|---|
| FP-001 | 2026-08-29 | Baseline | Morning issue contained 321 articles while the product promises a calm finite edition. | Open. Phase 2 introduces separate candidate retention and bounded issue selection. |
| FP-002 | 2026-08-29 | Baseline | Prototype categories do not match the seven live Notion Topic/Page options. | Open. Phase 1 imports owner pages; Phase 5 aligns navigation and presentation. |
| FP-003 | 2026-08-29 | Baseline | Feed configuration permits only one category per source. | Open. Phase 1 registry supports multiple topic/pages with one canonical reading item. |
| FP-004 | 2026-08-29 | Baseline | `why_selected` is generic and does not cite the owner rule that caused selection. | Open. Phase 2 adds reason codes and grounded explanations. |
| FP-005 | 2026-08-29 | Baseline | Afternoon exclusion can fail when a story's URL, headline, or cluster identity changes. | Open. Phase 3 adds stable story fingerprints and material-change classification. |
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
