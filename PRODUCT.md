# Daily Clipping Service — Product Contract

## Purpose

Produce a calm, finite, private information edition from the owner's approved
sources and coverage requirements. FreshRSS is ingestion infrastructure, not
the normal reading interface.

The reading surface must look and read as one coherent newspaper publication.
It must not reproduce the typography, navigation, widgets, advertisements, or
other visual fragments of source websites. Source identity appears as compact
provenance; the edition owns the masthead, typography, hierarchy, imagery,
summaries, and page composition.

## Access

- Responsive web application usable on phone, tablet, and desktop.
- Available at home and away through the owner's private Tailscale network.
- Reading state and actions synchronize across devices.

## Edition cadence

- One morning edition.
- One afternoon update.
- Edition times use America/Chicago and remain configurable until commissioned.
- The morning edition is the primary daily briefing.
- The afternoon edition contains new stories and material developments since
  the morning. It must not repeat unchanged morning material.
- An edition is an immutable snapshot after publication. Later corrections or
  developments appear in the next edition and may link back to the earlier
  story cluster.

## Organization

- Organize the edition by topic or theme, never by source.
- A story reported by multiple sources appears once as a story cluster.
- Source names and links appear as provenance within the cluster.
- Sections are derived from the owner's actual interests and Notion source
  guidance, not a generic news taxonomy.
- Empty sections are omitted.

## Story presentation

Each selected story provides:

- concise headline;
- short summary;
- why it was selected;
- publication time or material-update time;
- primary article link;
- additional corroborating/source links when useful;
- topic/theme;
- read, dismiss, and save actions.

The interface must have an explicit end and a clear “nothing material changed”
state.

## Navigation

- Current edition opens by default.
- Morning and afternoon issues are visibly distinguished.
- A Previous Editions tab lists prior editions newest-first.
- Previous editions remain readable as the snapshots originally published.
- Dates provide direct navigation to both issues when both exist.

## Selection rules

- Apply the owner's Must include, Avoid, and Sufficiency guidance.
- Prefer material developments over rewrites, reactions, and search-optimized
  repetition.
- Deduplicate semantically across sources.
- Rank by relevance and consequence, not source publishing volume.
- High-volume sources must not dominate an edition.
- A source is evidence and provenance; it is not an edition section.

## State and retention

- FreshRSS remains the synchronized ingestion/read-state engine.
- Edition snapshots, story clusters, selection explanations, and edition-level
  history live in the presentation service's own store.
- Read and dismiss affect the active reading experience without rewriting old
  edition snapshots.
- Save retains an item for the future durable archive layer.

## Not yet commissioned

- Exact morning and afternoon publication times.
- Final topic/theme vocabulary after observing the owner-grounded pilot.
- Retention duration for full edition snapshots.
- Final save/archive destination.
