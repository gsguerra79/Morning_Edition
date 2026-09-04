# The Forge Daily — v2 Roadmap

Last reconciled: 2026-09-03

This is the canonical post-v1 backlog. It replaces the deferred Stage 2–6 list
in `EXECUTION-PLAN.md`, which had become inaccurate as v1 work closed several
of those items. Work enters v2 only if it improves the owner-facing reader; an
adapter experiment or passing test is evidence, not delivery.

## Starting point

- v1.0.0 is owner-accepted and remains the immutable release baseline.
- The source inventory contains 33 unique canonical sources across seven pages.
- 32 sources are active and loaded. Kickstarter is the only genuine connector
  gap.
- Financial Times, Reuters, and World Surf League use working first-party
  sources. ATP Tour and Medium are live through compliant discovery feeds;
  better native integrations remain optional quality upgrades, not missing
  coverage.
- The production service already publishes immutable 07:30 morning and 16:30
  afternoon editions, maintains an archive, and filters unchanged afternoon
  rewrites. The rolling 49-story reader remains the accepted primary surface.

## Priority 1 — Make Sources the complete editorial control plane

**Outcome:** routine source governance moves fully into The Forge Daily, with
one canonical record per source and no need to edit the same truth in Notion.

- Edit canonical source name, URL, page assignments, **What I read here**,
  **Must include**, **Avoid**, and coverage/research status from the Sources
  view.
- Preserve the existing feed add/remove, validation, import/export, topic
  editing, aliases, and multi-feed health behavior.
- Add a deliberate source-research queue: request coverage, collect candidate
  sources, test them, and explicitly promote or reject them. Never auto-promote
  a discovered feed.
- Migrate the reconciled 33-source baseline once, validate it, and make Notion
  an optional reference/archive rather than a second writable authority.
- Provide recoverable export and conflict-safe persistence before retiring the
  routine Notion workflow.

**Acceptance:** Gabriel can change all editorial source guidance and request
new-source research in the normal Sources interface, then see the next issue
use those changes without developer or Notion intervention.

## Priority 2 — Close the sole source gap: Kickstarter

**Outcome:** useful crowdfunding and development-stage gear appears in the
paper without duplicating the existing Crowdfunding Daily Brief or importing
private backed-project administration.

- Reuse the existing cross-platform crowdfunding discovery and vetting work as
  the preferred upstream signal; do not build a second indiscriminate scraper.
- Define the safe handoff for public candidate stories into The Forge Daily.
- Admit only owner-fit technology, hardware, robotics, electronics,
  photography, computer/security accessories, compact tools, and tabletop
  projects.
- Keep pledge-manager messages, backed-project actions, and private account
  state in the existing brief workflow, outside the newspaper.
- Close the gap only when attributable current cards are visible and the
  canonical Kickstarter source reports healthy.

**Acceptance:** current, relevant projects appear reliably without campaign
spam or private-account material.

## Priority 3 — Turn the existing editions into a polished reading workflow

**Outcome:** the already-running morning and afternoon publication machinery
becomes as useful and legible as the accepted rolling reader.

- Keep the rolling issue as the default while making the latest immutable
  morning edition and afternoon update easy to enter and return from.
- Present the afternoon as **new**, **materially changed**, or **no material
  change**, with a clear link to its morning story when applicable.
- Apply accepted density, weather, comic, provenance, feedback, and read-state
  behavior consistently to archived editions.
- Review real consecutive morning/afternoon pairs for bounded volume,
  retention, duplicates, and source balance before calling the workflow done.

**Acceptance:** Gabriel can read and compare a real same-day pair on desktop
and phone and understand every afternoon inclusion without technical tools.

## Priority 4 — Offer selectable visual identities

**Outcome:** Gabriel can choose among coherent publication styles without
changing the underlying stories, ranking, source rules, or reader behavior.

- Keep the accepted **Modern Magazine** identity as the default.
- Add a **Traditional Broadsheet** identity with stronger column structure,
  classical newspaper typography, rules, folios, and denser headline hierarchy.
- Add an **Editorial Journal** identity with restrained spacing, larger imagery,
  and a calmer long-form reading emphasis.
- Add a **Newsroom Dashboard** identity with higher information density, compact
  cards, faster scanning, and stronger live-status treatment.
- Retain light/dark mode within each identity where contrast and legibility can
  be maintained honestly.
- Store the selected identity as a synchronized preference and apply it to the
  rolling issue, topic pages, weather, sources, editions, feedback, and settings.
- Build the identities from shared design tokens and layout components so new
  features cannot drift into four unrelated interfaces.

**Acceptance:** Gabriel can switch among all four identities in the normal
reader on desktop and phone; every view remains complete, readable, responsive,
and functionally identical, and the choice persists across devices.

## Priority 5 — Add topic-specific cards where structure adds value

**Outcome:** structured subjects stop looking like generic articles.

- **ATP and WSL:** event status, upcoming schedule, results, ranking/standings
  context, and relevant Brazilian competitors when available.
- **Formula 1:** fact, analysis, rumor, or informed-speculation labels plus
  driver, team, and event context.
- **Crowdfunding and development-stage gear:** campaign status, evidence,
  maker record, readiness, delivery risk, support outlook, and landed-cost
  concerns when the source supports them. This follows Priority 2.
- Retain the accepted two-comic artwork cards; further comic work is optional
  polish, not an outstanding requirement.

**Acceptance:** real examples of each structured format are visibly more useful
than the ordinary article card and remain clean on desktop and phone.

## Priority 6 — Optional connector-quality upgrades

These are upgrades to active coverage, not blockers and not a reason to delay
the priorities above.

- Replace ATP discovery with a first-party structured news/schedule/results
  integration if a reliable compliant endpoint is available.
- Consider Reuters Connect only if Gabriel's authorized access would add useful
  licensed metadata beyond the current first-party news sitemap.
- Replace Medium public topic feeds with Gabriel's authenticated followed-topic
  stream only if it can be accessed reliably and compliantly.
- Financial Times and World Surf League require monitoring, not replacement,
  while their current first-party connections remain healthy.

## Priority 7 — Operational finish

**Outcome:** recovery and failures are owner-visible and routinely proven.

- Add actionable publication/source failure alerts without noisy success mail.
- Automate encrypted runtime backups for state and immutable editions, with
  retention appropriate to the private host.
- Run and record a current disposable restore drill, including edition
  checksums and shared reading state.
- Verify host restart, upstream outage, partial connector failure, and rollback
  behavior without corrupting the live archive.

**Acceptance:** a current backup restores successfully and meaningful failures
surface clearly in the reader or through a concise alert.

## Removed from the outstanding backlog

The following work is already delivered in v1 or the post-release source fix:

- rebuilding Financial Times, World Surf League, ATP, Reuters, and Medium as if
  all were missing;
- seven-page navigation, full All-page density, and 49-story balanced layout;
- two current artwork-backed comic cards;
- Celsius weather and the Houston/Rio weather desk;
- optional hide-on-open, feedback, Read Later, and cross-device state;
- basic in-product feed/topic management and visible source health;
- immutable scheduled publication, archive storage, and afternoon
  material-change filtering;
- consolidation of runtime feed variants into 33 canonical source records.

## Execution order

Start with Priority 1. Complete one owner-verifiable slice at a time and obtain
explicit acceptance before opening the next priority. Priority 6 may be
investigated opportunistically but must not displace owner-facing work.
