"""Deterministic, auditable selection of a finite newspaper issue."""

import math
import re
from datetime import datetime

DEFAULT_PAGE_CAPS = {
    "worldnews": 12, "usnews": 12, "brazilnews": 8, "formula1": 12,
    "technologythings": 10, "comics": 2, "sports": 12, "ideas": 5,
    # Legacy keys remain bounded while carried articles are being remapped.
    "technology": 10, "photography": 5, "outdoors": 5,
    "f1": 12, "world": 8,
}
DEFAULT_PAGE_MINIMUMS = {"brazilnews": 6}
SOURCE_ALIASES = {
    "bbc world": "BBC", "bbc science & environment": "BBC",
    "bbc technology": "BBC", "bbc formula 1": "BBC",
    "bbc us & canada": "BBC",
    "financial times us": "Financial Times",
    "financial times world": "Financial Times",
    "new york times us": "New York Times",
    "new york times world": "New York Times",
    "motorsport f1": "Motorsport", "g1 brasil": "Globo",
    "autosport f1": "Autosport",
    "the order of the stick": "GiantITP",
}
REQUIRED_PAGE_SOURCES = {
    "worldnews": ("bbc world", "financial times world", "reuters", "new york times world"),
    "usnews": ("bbc us & canada", "financial times us", "reuters",
               "new york times us", "washington post", "houston chronicle"),
    "brazilnews": ("globo", "agência brasil", "agência pública",
                   "((o))eco", "rioonwatch"),
    "sports": ("atp tour", "world surf league"),
    "comics": ("giantitp", "wilde life"),
    "formula1": ("formula 1", "motorsport", "autosport"),
}
RAW_SOURCE_LIMITS = {
    "bbc us & canada": 3,
    "financial times us": 3,
    "financial times world": 3,
    "reuters": 6,
    "atp tour": 2,
    "world surf league": 3,
    "giantitp": 1,
    "wilde life": 1,
    "formula 1": 3,
    "motorsport": 3,
    "autosport": 3,
    "racefans": 2,
    "the race": 2,
}
F1_KIND_MINIMUMS = {"results_updates": 3, "technical": 2,
                    "preview_forecast": 1, "news": 2}
F1_KIND_MAXIMUMS = {"rumor_interview": 3}


def f1_kind(article):
    text = _text(article)
    if re.search(r"\b(results?|classification|standings|practice\s*[123]?|fp[123]|qualifying|"
                 r"sprint(?:\s+race)?|grid|penalt(?:y|ies)|race result|live coverage|as it happened)\b", text):
        return "results_updates"
    if _matches(text, ("technical", "technology", "upgrade", "engine", "power unit",
                       "aero", "regulation", "rule", "tyre", "tire", "battery",
                       "chassis", "floor", "wing", "design", "top speed")):
        return "technical"
    if _matches(text, ("preview", "forecast", "weather", "heat", "what to expect",
                       "prediction", "chances", "weekend", "grand prix", " gp ")):
        return "preview_forecast"
    if _matches(text, ("rumor", "rumour", "interview", "reveals", "admits", "warns",
                       "says", "why ", "future", "contract", "driver market")):
        return "rumor_interview"
    return "news"


def _text(article):
    return " ".join(str(article.get(key) or "")
                    for key in ("title", "summary", "feed_summary")).casefold()


def _matches(text, phrases):
    return any(str(phrase).casefold() in text for phrase in phrases or [] if phrase)


def _registry_index(registry):
    return {str(item.get("source") or "").casefold(): item
            for item in (registry or {}).get("sources", []) if item.get("source")}


def _source_record(source, index):
    key = str(source or "").casefold()
    canonical = SOURCE_ALIASES.get(key, source)
    return index.get(str(canonical or "").casefold())


def _score(article):
    return float(article.get("score") or 0) + float(article.get("cluster_boost") or 0) + \
        float(article.get("taste_boost") or 0)


def _published_rank(article):
    try:
        return datetime.fromisoformat(str(article.get("published_at") or "").replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return 0


def _page_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _reason(article, source_record, mandatory=False):
    source = (source_record or {}).get("source") or article.get("source") or "an approved source"
    category = str(article.get("category") or "your interests").replace("-", " ")
    if mandatory:
        return f"Must include: matched the owner's required coverage from {source}."
    guidance = str((source_record or {}).get("what_i_read") or "").strip()
    if guidance:
        first = re.split(r"[.;]", guidance, maxsplit=1)[0].strip()
        return f"Selected from {source} for {category}: {first[:140]}."
    if int(article.get("cluster_size") or 1) > 1:
        return f"Selected for {category}; grouped with related coverage."
    return f"Selected as timely coverage of {category} from {source}."


def select_issue(articles, registry=None, rules=None, max_stories=80,
                 source_share=0.20, page_caps=None, page_minimums=None):
    """Return ``(selected, report)``; one representative per story cluster."""
    page_caps = {**DEFAULT_PAGE_CAPS, **(page_caps or {})}
    page_minimums = {**DEFAULT_PAGE_MINIMUMS, **(page_minimums or {})}
    source_limit = max(1, math.ceil(max_stories * source_share))
    index = _registry_index(registry)
    rule_map = (rules or {}).get("sources", {}) if isinstance(rules, dict) else {}
    candidates, rejected, seen_clusters = [], [], set()
    cluster_sources = {}

    for article in articles or []:
        cluster = article.get("cluster_id") or article.get("id")
        if not cluster:
            continue
        source = article.get("source")
        url = article.get("url")
        if source or url:
            cluster_sources.setdefault(cluster, []).append({
                "source": source, "title": article.get("title"), "url": url,
            })

    for position, article in enumerate(articles or []):
        if article.get("cluster_rep") is False:
            continue
        cluster = article.get("cluster_id") or article.get("id") or f"row-{position}"
        if cluster in seen_clusters:
            continue
        seen_clusters.add(cluster)
        source = article.get("source")
        record = _source_record(source, index)
        canonical = (record or {}).get("source") or source or "Unknown"
        source_rules = (rule_map.get(str(source or "")) or rule_map.get(canonical, {})
                        if isinstance(rule_map, dict) else {})
        text = _text(article)
        excluded = _matches(text, source_rules.get("exclude_any"))
        unless = source_rules.get("exclude_unless_any") or []
        if excluded and unless and _matches(text, unless):
            excluded = False
        if excluded:
            rejected.append({"id": article.get("id"), "code": "source_avoid_rule",
                             "source": canonical})
            continue
        required = source_rules.get("require_any") or []
        if required and not _matches(text, required):
            rejected.append({"id": article.get("id"), "code": "outside_source_scope",
                             "source": canonical})
            continue
        mandatory = _matches(text, source_rules.get("must_any"))
        item = dict(article)
        item["editorial_source"] = canonical
        # The ingestion pipeline owns article-level routing.  This matters for
        # multi-desk publishers (Reuters, BBC, FT, NYT): a source-level ledger
        # topic is only a fallback for old/unclassified input and must never
        # overwrite an explicit US/World assignment during edition publishing.
        topics = (record or {}).get("topics") or []
        if not item.get("category") and topics:
            item["category"] = _page_key(topics[0])
        if not item.get("category") and source_rules.get("category"):
            item["category"] = _page_key(source_rules["category"])
        item["editorial_must_include"] = mandatory
        if item.get("category") in ("formula1", "f1"):
            item["f1_kind"] = f1_kind(item)
        item["selection_score"] = round(_score(item), 4)
        item["why_selected"] = _reason(item, record, mandatory)
        corroborating = []
        seen_evidence = set()
        for evidence in cluster_sources.get(cluster, []):
            evidence_record = _source_record(evidence.get("source"), index)
            evidence_source = (evidence_record or {}).get("source") or evidence.get("source")
            if str(evidence_source or "").casefold() == str(canonical).casefold():
                continue
            identity = (evidence.get("source"), evidence.get("url"))
            if identity in seen_evidence or (evidence.get("url") and evidence.get("url") == item.get("url")):
                continue
            seen_evidence.add(identity)
            corroborating.append(evidence)
        if corroborating:
            item["corroborating_sources"] = corroborating
        candidates.append(item)

    candidates.sort(key=lambda item: (
        not item["editorial_must_include"], -item["selection_score"],
        -_published_rank(item), str(item.get("id") or "")))
    selected, selected_ids = [], set()
    source_counts, raw_source_counts, page_counts, f1_kind_counts = {}, {}, {}, {}

    def add(item):
        identity = item.get("id") or item.get("cluster_id")
        if identity in selected_ids:
            return False
        selected_ids.add(identity)
        selected.append(item)
        source = item["editorial_source"]
        raw_source = str(item.get("source") or "").casefold()
        page = item.get("category") or "other"
        source_counts[source] = source_counts.get(source, 0) + 1
        raw_source_counts[raw_source] = raw_source_counts.get(raw_source, 0) + 1
        page_counts[page] = page_counts.get(page, 0) + 1
        if page in ("formula1", "f1"):
            kind = item.get("f1_kind") or f1_kind(item)
            f1_kind_counts[kind] = f1_kind_counts.get(kind, 0) + 1
        return True

    for item in candidates:
        if item["editorial_must_include"]:
            add(item)

    # Named source promises are stronger than a page's generic score order.
    # Reserve one current card from each before high-volume sources consume the
    # page cap. Comics are special: one latest card from each series, period.
    for page, required_sources in REQUIRED_PAGE_SOURCES.items():
        for raw_source in required_sources:
            matches = [candidate for candidate in candidates
                       if (candidate.get("category") or "other") == page
                       and str(candidate.get("source") or "").casefold() == raw_source]
            if matches and not any(str(item.get("source") or "").casefold() == raw_source
                                   for item in selected):
                newest = max(matches, key=lambda item: str(item.get("published_at") or ""))
                if len(selected) < max_stories:
                    add(newest)

    for page in sorted({item.get("category") or "other" for item in candidates}):
        if page_counts.get(page, 0):
            continue
        item = next((candidate for candidate in candidates
                     if (candidate.get("category") or "other") == page
                     and source_counts.get(candidate["editorial_source"], 0) < source_limit), None)
        if item and len(selected) < max_stories:
            add(item)

    # A race desk needs reporting modes, not twelve variants of the same quote.
    # Reserve results/live updates, engineering, previews and straight news
    # before generic score order fills the remaining Formula 1 slots.
    f1_candidates = [item for item in candidates
                     if item.get("category") in ("formula1", "f1")]
    for kind, minimum in F1_KIND_MINIMUMS.items():
        for item in (candidate for candidate in f1_candidates
                     if candidate.get("f1_kind") == kind):
            if f1_kind_counts.get(kind, 0) >= minimum or len(selected) >= max_stories:
                break
            page = item.get("category") or "formula1"
            if page_counts.get(page, 0) >= page_caps.get(page, max_stories):
                break
            raw_source = str(item.get("source") or "").casefold()
            if raw_source_counts.get(raw_source, 0) >= RAW_SOURCE_LIMITS.get(raw_source, max_stories):
                continue
            add(item)

    # A global issue limit must not starve a promised desk merely because its
    # stories rank below high-volume technology or sports feeds. Reserve each
    # configured page floor before the ordinary global score pass.
    for page, minimum in page_minimums.items():
        for item in (candidate for candidate in candidates
                     if (candidate.get("category") or "other") == page):
            if page_counts.get(page, 0) >= minimum or len(selected) >= max_stories:
                break
            raw_source = str(item.get("source") or "").casefold()
            source = item["editorial_source"]
            if source_counts.get(source, 0) >= source_limit:
                continue
            if raw_source_counts.get(raw_source, 0) >= RAW_SOURCE_LIMITS.get(raw_source, max_stories):
                continue
            if page_counts.get(page, 0) >= page_caps.get(page, max_stories):
                break
            add(item)

    for item in candidates:
        if len(selected) >= max_stories and not item["editorial_must_include"]:
            break
        identity = item.get("id") or item.get("cluster_id")
        if identity in selected_ids:
            continue
        if item["editorial_must_include"]:
            continue
        source = item["editorial_source"]
        raw_source = str(item.get("source") or "").casefold()
        page = item.get("category") or "other"
        if page == "comics":
            # The two requested comic subscriptions were already anchored
            # above; older installments must not fill spare issue capacity.
            continue
        if source_counts.get(source, 0) >= source_limit:
            rejected.append({"id": item.get("id"), "code": "source_cap", "source": source})
            continue
        if raw_source_counts.get(raw_source, 0) >= RAW_SOURCE_LIMITS.get(raw_source, max_stories):
            rejected.append({"id": item.get("id"), "code": "source_variant_cap",
                             "source": item.get("source")})
            continue
        if page in ("formula1", "f1"):
            kind = item.get("f1_kind") or f1_kind(item)
            if f1_kind_counts.get(kind, 0) >= F1_KIND_MAXIMUMS.get(kind, max_stories):
                rejected.append({"id": item.get("id"), "code": "f1_kind_cap",
                                 "kind": kind})
                continue
        if page_counts.get(page, 0) >= page_caps.get(page, max_stories):
            rejected.append({"id": item.get("id"), "code": "page_cap", "page": page})
            continue
        add(item)

    selected.sort(key=lambda item: (-item["selection_score"], str(item.get("id") or "")))
    report = {
        "candidate_stories": len(candidates), "selected_stories": len(selected),
        "mandatory_stories": sum(1 for item in selected if item["editorial_must_include"]),
        "source_limit": source_limit, "source_counts": source_counts,
        "page_counts": page_counts, "rejected": rejected,
        "f1_kind_counts": f1_kind_counts,
    }
    return selected, report
