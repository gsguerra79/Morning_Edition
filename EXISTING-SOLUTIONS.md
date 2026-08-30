# Existing-solutions preflight

Evaluated 2026-08-24 against the Daily Clipping Service product contract.

## Verdict

No existing product satisfies the entire contract unchanged. Do not build the
ranking, summarization, semantic clustering, or magazine layout from scratch.
Use Cruxwire as the leading reusable foundation, retain FreshRSS only where its
connector/state value remains useful, and add the missing edition-publication
model and newspaper identity deliberately.

## Cruxwire — leading foundation

Status: **PARTIAL, strongest fit**

Validated from source and a local throwaway render:

- coherent magazine front page rather than source-fragment rendering;
- configurable topic categories with interest descriptions;
- LLM relevance scoring and summaries;
- embedding-based cross-source story clustering;
- one representative card with supporting coverage collapsed beneath it;
- read, dismiss, Read Later, History, semantic search, and shared device state;
- one-container, MIT-licensed, self-hosted design.

Missing or wrong for this service:

- rolling digest rather than published morning/afternoon issues;
- History means articles opened, not immutable previous editions;
- no Previous Editions calendar/archive;
- no explicit morning-versus-afternoon delta contract;
- selection explanation is not a first-class story field;
- direct feed ingestion duplicates some FreshRSS plumbing;
- no login, acceptable only behind the private Tailscale boundary;
- very young project with a small maintainer/user base.

## NewsBlur Daily Briefing

Status: **PARTIAL, strongest turnkey behavior**

- scores and summarizes the owner's feeds;
- sections, classifiers, keyword interests, and “why selected” pills;
- story clustering;
- scheduled once, twice, or three times daily;
- same-day briefing windows do not repeat stories;
- native web and mobile access.

Weaknesses:

- the briefing remains a feature inside an RSS reader rather than a standalone
  single-publication newspaper;
- built-in sections are workflow/source-behavior concepts such as Top Stories,
  infrequent sites, and long reads rather than solely the owner's themes;
- no evidence of an immutable issue archive matching the required Previous
  Editions experience;
- full Daily Briefing requires the hosted Premium Archive tier; self-hosting the
  full NewsBlur stack is substantially heavier than this household service.

## Firstlight

Status: **PARTIAL, visual reference only**

- strongest literal single-publication/printed-page identity;
- finite one-sheet morning paper;
- PDF archive and responsive preview;
- active, MIT-licensed Docker project.

Weaknesses:

- one daily issue only;
- headline list rather than summaries, clustering, ranking explanations, and
  interactive story actions;
- archive is PDFs;
- weather/calendar/to-do/printing product, not a topic-led news edition.

Use its restraint, masthead, typography, rules, whitespace, and finite-page
discipline as visual reference, not as the application core.

## News Router

Status: **PARTIAL, not selected**

- explicit topic groups;
- morning and evening scheduled digests;
- edition window and archive mechanics;
- self-hosted FastAPI/Svelte stack.

Weaknesses:

- list/reels reader presentation rather than a unified newspaper;
- archive stores old articles rather than faithful issue snapshots;
- no semantic cross-source clustering or editorial synthesis comparable to
  Cruxwire;
- created recently, zero stars/forks, no declared repository license metadata,
  and only a handful of initial commits.

## Rejected as primary solutions

- RSSPub: EPUB newspaper output, not the required interactive web edition.
- Feed2040: conventional three-pane RSS reader with AI briefing bolted on.
- Readeck/Karakeep/Linkwarden: reading archives rather than daily editions.
- Inoreader/Feedly: powerful ingestion and rules, but continuous reader/inbox
  products without the required single-publication issue experience.

## Reuse boundary

Reuse from Cruxwire:

- magazine layout and responsive interaction patterns;
- scoring, summarization, embeddings, semantic clustering, category model;
- read/dismiss/save state and search;
- feed-validation and pipeline patterns where FreshRSS does not already own the
  job.

Add for this service:

- edition database with immutable issue and story-cluster snapshots;
- morning and afternoon issue publisher with no-repeat/material-change rules;
- Previous Editions tab and date/issue navigation;
- explicit “why selected” copy;
- owner-specific masthead and newspaper design system;
- FreshRSS/Notion adapters and private Tailscale deployment.
