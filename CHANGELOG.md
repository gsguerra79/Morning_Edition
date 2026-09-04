# Changelog

## Unreleased

- Correct the Formula 1 page hierarchy: prefer the newest finalized OpenF1
  session over a lagging archive result, align the compact session card with an
  unclipped top-right championship rail, and admit only concrete on-track,
  strategy, personnel, technical, or incident reporting to the Race Desk tier.

- Add an optional authenticated OpenF1 current-session layer to the Formula 1
  race desk. During OpenF1's live window it supplies a compact provisional
  classification and track weather; the existing Formula 1 archive and Jolpica
  providers remain independent fallbacks. Credentials stay backend-only.

- Rebuild Formula 1 as a race desk: current driver and constructor championship
  tables, the latest finalized race-weekend session classification, next-session
  timing, and twelve balanced dedicated-page stories while Home remains capped
  at six. Add Autosport, protect Motorsport and Autosport representation, label
  reporting type, and limit rumor/interview filler.
- Remove the visible “Why it’s here” paragraph from story cards while retaining
  the selection explanation in edition data for audit and future detail views.
- Replace Reuters' image-less Google News discovery with its first-party news
  sitemap and route FT/Reuters artwork through a tightly allow-listed same-origin
  image relay. Use restrained source artwork when either publisher supplies no
  story photograph.
- Replace the inherited abstract browser icon with a Forge Daily hammer-and-anvil
  favicon, including SVG, PNG, ICO, and Apple touch variants plus cache-busted
  browser references.
- Replace the stale deferred Stage 2–6 list with a reconciled v2 roadmap that
  distinguishes the sole missing source, active-source quality upgrades, and
  already-delivered v1 behavior.
- Prioritize complete in-reader editorial source governance, the Kickstarter
  gap, edition workflow polish, four selectable visual identities, structured
  sports/F1/crowdfunding cards, and operational recovery proof.
- Consolidate descriptive runtime feed labels into their canonical source record
  in Sources, preserving editorial guidance while showing every active endpoint.
- Keep each canonical source to one inventory card even when it serves multiple
  paper pages; show its page assignments and feed count on that card.
- Reconcile the existing Notion source rows with current connection status and
  page assignments without creating duplicate records.

## v1.0.0 — 2026-09-03

First owner-accepted release of The Forge Daily.

- A balanced 49-story rolling issue across seven topic pages.
- Full-width, gap-free All-page layout on desktop and responsive phone layout.
- BBC US, Financial Times, Reuters, ATP Tour, World Surf League, LEGO, and the
  wider approved source set represented in the live ingestion and selection.
- Two current comic cards with cropped artwork from the original comic pages.
- Houston current, hourly, weekly, radar, alert, and severe-weather coverage in
  Celsius, plus a compact Rio de Janeiro current-weather card.
- In-product source inventory, source management, and topic controls.
- Cross-device reading state, feedback, Read Later, and optional hide-on-open.

The remaining staged expansion work in `EXECUTION-PLAN.md` is a post-v1 roadmap
and is not claimed as part of this release.
