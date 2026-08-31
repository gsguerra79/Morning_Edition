"""Deterministic, auditable selection of a finite newspaper issue."""

import math
import re

DEFAULT_PAGE_CAPS = {
    "brazilnews": 6, "worldnews": 8, "formula1": 6,
    "technologythings": 8, "comics": 2, "sports": 5, "ideas": 5,
    # Legacy keys remain bounded while carried articles are being remapped.
    "technology": 8, "photography": 5, "outdoors": 5,
    "f1": 6, "world": 8,
}
SOURCE_ALIASES = {
    "bbc world": "BBC", "bbc science & environment": "BBC",
    "bbc technology": "BBC", "bbc formula 1": "BBC",
    "motorsport f1": "Motorsport", "g1 brasil": "Globo",
    "the order of the stick": "GiantITP",
}


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


def select_issue(articles, registry=None, rules=None, max_stories=40,
                 source_share=0.20, page_caps=None):
    """Return ``(selected, report)``; one representative per story cluster."""
    page_caps = {**DEFAULT_PAGE_CAPS, **(page_caps or {})}
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
        record = _source_record(article.get("source"), index)
        canonical = (record or {}).get("source") or article.get("source") or "Unknown"
        source_rules = rule_map.get(canonical, {}) if isinstance(rule_map, dict) else {}
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
        topics = (record or {}).get("topics") or []
        if topics:
            item["category"] = _page_key(topics[0])
        item["editorial_must_include"] = mandatory
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
        str(item.get("published_at") or ""), str(item.get("id") or "")))
    selected, selected_ids = [], set()
    source_counts, page_counts = {}, {}

    def add(item):
        identity = item.get("id") or item.get("cluster_id")
        if identity in selected_ids:
            return False
        selected_ids.add(identity)
        selected.append(item)
        source = item["editorial_source"]
        page = item.get("category") or "other"
        source_counts[source] = source_counts.get(source, 0) + 1
        page_counts[page] = page_counts.get(page, 0) + 1
        return True

    for item in candidates:
        if item["editorial_must_include"]:
            add(item)

    for page in sorted({item.get("category") or "other" for item in candidates}):
        if page_counts.get(page, 0):
            continue
        item = next((candidate for candidate in candidates
                     if (candidate.get("category") or "other") == page
                     and source_counts.get(candidate["editorial_source"], 0) < source_limit), None)
        if item and len(selected) < max_stories:
            add(item)

    for item in candidates:
        if len(selected) >= max_stories and not item["editorial_must_include"]:
            break
        if item["editorial_must_include"]:
            continue
        source = item["editorial_source"]
        page = item.get("category") or "other"
        if source_counts.get(source, 0) >= source_limit:
            rejected.append({"id": item.get("id"), "code": "source_cap", "source": source})
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
    }
    return selected, report
