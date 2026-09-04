"""Owner-facing reconciliation of editorial scope and live ingestion."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit


PAGE_DEFINITIONS = {
    "Brazil News": {"key": "brazilnews", "color": "#2f6f56",
                    "interest": "Consequential Brazil news, federal policy, Rio de Janeiro, environment, wildlife and relevant national sports"},
    "World News": {"key": "worldnews", "color": "#315b78",
                   "interest": "Consequential international news and analysis"},
    "Formula 1": {"key": "formula1", "color": "#a52a2a",
                  "interest": "Formula 1 news, races, rules, teams, drivers, engineering and analysis"},
    "Technology & Things": {"key": "technology", "color": "#79632f",
                            "interest": "Novel technology, ingenious gear, photography, electronics, fabrication and advanced projects"},
    "Comics": {"key": "comics", "color": "#8b5267",
               "interest": "Selected webcomics"},
    "Sports": {"key": "sports", "color": "#46634a",
               "interest": "Tennis, surfing, climbing, mountaineering and expeditions, with Brazilian competitors where relevant"},
    "Ideas": {"key": "ideas", "color": "#76538c",
              "interest": "Substantive essays, science, philosophy, psychology and durable explanatory ideas"},
}

SOURCE_ALIASES = {
    "bbc world": "BBC", "bbc us & canada": "BBC",
    "bbc science & environment": "BBC", "bbc technology": "BBC",
    "bbc football": "BBC", "bbc formula 1": "BBC",
    "financial times us": "Financial Times",
    "financial times world": "Financial Times",
    "ge flamengo": "Globo",
    "medium technology": "Medium",
}


def _canonical_source(value):
    source = str(value or "").strip()
    return SOURCE_ALIASES.get(source.casefold(), source)


def _url(value):
    try:
        parts = urlsplit(str(value or "").strip())
    except ValueError:
        return ""
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return ""
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/"), parts.query, ""))


def _rule_state(rules):
    if not isinstance(rules, dict) or not rules:
        return "missing"
    return "loaded" if isinstance(rules.get("sources"), dict) else "invalid"


def runtime_scope(registry):
    """Compile the complete active registry into runtime categories and feeds."""
    sources = (registry or {}).get("sources") or []
    categories = [dict(key=spec["key"], label=page, color=spec["color"],
                       interest=spec["interest"])
                  for page, spec in PAGE_DEFINITIONS.items()]
    feeds = []
    for source in sources:
        topics = source.get("topics") or []
        page = next((topic for topic in topics if topic in PAGE_DEFINITIONS), None)
        if not page:
            continue
        for adapter in source.get("adapters") or []:
            if adapter.get("status") != "active" or adapter.get("type") != "rss" or not adapter.get("url"):
                continue
            feeds.append({"url": adapter["url"], "source": source["source"],
                          "category": PAGE_DEFINITIONS[page]["key"]})
            if adapter.get("label"):
                feeds[-1]["source"] = adapter["label"]
    feeds.sort(key=lambda item: (item["source"].casefold(), item["url"]))
    return categories, feeds


def build(registry, feeds, digest=None, rules=None):
    sources = registry.get("sources") if isinstance(registry, dict) else None
    registry_loaded = isinstance(sources, list) and bool(sources)
    sources = sources or []
    feeds = [feed for feed in (feeds or []) if isinstance(feed, dict)]
    configured_urls = {_url(feed.get("url")) for feed in feeds
                       if isinstance(feed, dict)}
    registry_urls = {
        _url(adapter.get("url"))
        for source in sources
        for adapter in (source.get("adapters") or [])
        if isinstance(adapter, dict) and adapter.get("url")
    }
    article_counts = Counter()
    feed_health = {_url(item.get("url")): item for item in (digest or {}).get("feed_health", [])
                   if isinstance(item, dict) and item.get("url")}
    for article in (digest or {}).get("articles", []):
        if isinstance(article, dict):
            raw = str(article.get("editorial_source") or article.get("source") or "")
            article_counts[_canonical_source(raw)] += 1

    rows = []
    for source in sources:
        adapters = source.get("adapters") or []
        active = [adapter for adapter in adapters
                  if adapter.get("status") == "active"]
        active_urls = [_url(adapter.get("url")) for adapter in active
                       if adapter.get("url")]
        configured = sum(1 for url in active_urls if url in configured_urls)
        planned = any(adapter.get("status") == "planned" for adapter in adapters)
        blocked = any(adapter.get("status") == "blocked" for adapter in adapters)
        if blocked:
            adapter_state = "blocked"
        elif active:
            adapter_state = "active"
        elif planned:
            adapter_state = "connector-needed"
        else:
            adapter_state = "missing"
        if active and configured == len(active_urls):
            ingestion_state = "loaded"
        elif active and configured:
            ingestion_state = "partial"
        elif active:
            ingestion_state = "not-loaded"
        else:
            ingestion_state = "waiting"
        observed = [feed_health.get(url) for url in active_urls if url]
        if not active:
            health_state = "waiting-for-connector"
        elif not observed or any(item is None for item in observed):
            health_state = "not-checked"
        elif any(item.get("status") == "failed" for item in observed):
            health_state = "fetch-failed"
        elif sum(int(item.get("items") or 0) for item in observed):
            health_state = "healthy"
        else:
            health_state = "healthy-no-recent-items"
        rows.append({
            "source": source.get("source"),
            "topics": source.get("topics") or [],
            "what_i_read": source.get("what_i_read"),
            "must_include": source.get("must_include"),
            "avoid": source.get("avoid"),
            "sufficiency": source.get("sufficiency"),
            "adapter_state": adapter_state,
            "ingestion_state": ingestion_state,
            "active_adapters": len(active_urls),
            "configured_adapters": configured,
            "health_state": health_state,
            "current_items": article_counts.get(str(source.get("source") or ""), 0),
            "origin": "editorial-registry",
        })

    # A source added directly in the reader must immediately appear in its
    # inventory even though it was never part of the imported Notion baseline.
    # Match by adapter URL first so labeled sub-feeds (BBC US, BBC Tennis, etc.)
    # do not become duplicate pseudo-sources.
    page_by_key = {spec["key"]: page for page, spec in PAGE_DEFINITIONS.items()}
    runtime_only = {}
    for feed in feeds:
        url = _url(feed.get("url"))
        if not url or url in registry_urls:
            continue
        source = _canonical_source(feed.get("source"))
        if not source:
            continue
        item = runtime_only.setdefault(source, {"urls": [], "category": feed.get("category")})
        item["urls"].append(url)
    for source, item in runtime_only.items():
        observed = [feed_health.get(url) for url in item["urls"]]
        if not observed or any(health is None for health in observed):
            health_state = "not-checked"
        elif any(health.get("status") == "failed" for health in observed):
            health_state = "fetch-failed"
        elif sum(int(health.get("items") or 0) for health in observed):
            health_state = "healthy"
        else:
            health_state = "healthy-no-recent-items"
        rows.append({
            "source": source,
            "topics": [page_by_key.get(str(item["category"] or ""), "Unassigned")],
            "what_i_read": None,
            "must_include": None,
            "avoid": None,
            "sufficiency": "Added in The Forge Daily",
            "adapter_state": "active",
            "ingestion_state": "loaded",
            "active_adapters": len(item["urls"]),
            "configured_adapters": len(item["urls"]),
            "health_state": health_state,
            "current_items": article_counts.get(source, 0),
            "origin": "reader",
        })

    # Runtime endpoints may use a descriptive label (BBC US & Canada, FT World,
    # GE Flamengo) while the editorial registry holds the owner's canonical
    # source and its guidance. Merge those records here: one owner-facing source,
    # all working endpoints, and the detailed editorial instructions preserved.
    consolidated = {}
    health_priority = {
        "fetch-failed": 5, "not-checked": 4, "healthy": 3,
        "healthy-no-recent-items": 2, "waiting-for-connector": 1,
    }
    for row in rows:
        name = _canonical_source(row.get("source"))
        existing = consolidated.get(name)
        if existing is None:
            item = dict(row)
            item["source"] = name
            item["topics"] = list(dict.fromkeys(row.get("topics") or []))
            consolidated[name] = item
            continue
        existing["topics"] = list(dict.fromkeys(
            (existing.get("topics") or []) + (row.get("topics") or [])))
        for field in ("what_i_read", "must_include", "avoid", "sufficiency"):
            if not existing.get(field) and row.get(field):
                existing[field] = row[field]
        existing["active_adapters"] += row.get("active_adapters") or 0
        existing["configured_adapters"] += row.get("configured_adapters") or 0
        existing["adapter_state"] = (
            "active" if existing["active_adapters"] else existing["adapter_state"])
        if existing["active_adapters"]:
            existing["ingestion_state"] = (
                "loaded" if existing["configured_adapters"] == existing["active_adapters"]
                else "partial" if existing["configured_adapters"] else "not-loaded")
        if row.get("active_adapters") and health_priority.get(
                row.get("health_state"), 0) > health_priority.get(existing.get("health_state"), 0):
            existing["health_state"] = row["health_state"]
        existing["current_items"] = max(
            existing.get("current_items") or 0, row.get("current_items") or 0)
        if row.get("origin") == "editorial-registry":
            existing["origin"] = "editorial-registry"
    rows = list(consolidated.values())

    # A source is one inventory record even when it serves several paper pages.
    # Its full topic list remains on the card; the first owner topic determines
    # where that single card is filed.
    pages = {}
    for row in rows:
        topic = (row["topics"] or ["Unassigned"])[0]
        pages.setdefault(topic, []).append(row)
    pages = [{"page": name, "sources": sorted(items, key=lambda item: item["source"].casefold())}
             for name, items in sorted(pages.items())]
    rule_state = _rule_state(rules)
    warnings = []
    if not registry_loaded:
        warnings.append("The live editorial registry is missing or empty.")
    if rule_state != "loaded":
        warnings.append("The structured selection rules are not loaded; editorial filtering will fall back.")
    not_loaded = [row["source"] for row in rows if row["ingestion_state"] in ("not-loaded", "partial")]
    if not_loaded:
        warnings.append(f"{len(not_loaded)} active sources are not fully loaded into production.")
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "registry": {
            "status": "loaded" if registry_loaded else "missing",
            "generated_at": registry.get("generated_at") if isinstance(registry, dict) else None,
            "source_count": len(rows),
        },
        "rules": {"status": rule_state},
        "summary": {
            "sources": len(rows),
            "pages": len(pages),
            "active": sum(row["adapter_state"] == "active" for row in rows),
            "connector_gaps": sum(row["adapter_state"] != "active" for row in rows),
            "fully_loaded": sum(row["ingestion_state"] == "loaded" for row in rows),
        },
        "warnings": warnings,
        "pages": pages,
    }
