"""Stable story identity and auditable afternoon change classification."""

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "with",
    "after", "amid", "new", "latest", "live", "update", "updates",
}
STATE_GROUPS = {
    "rumor": {"rumor", "rumored", "rumour", "rumoured", "reported", "reportedly", "expected", "could", "may"},
    "confirmed": {"confirmed", "official", "announced", "signs", "signed", "wins", "won"},
    "correction": {"correction", "corrected", "retracted", "clarifies", "clarified"},
    "cancelled": {"cancelled", "canceled", "postponed", "suspended"},
}


def normalize_url(url):
    """Remove fragments, tracking, cosmetic host/path variants, and query order."""
    try:
        parts = urlsplit(str(url or "").strip())
    except ValueError:
        return ""
    host = (parts.hostname or "").casefold()
    if not host:
        return ""
    if host.startswith("www."):
        host = host[4:]
    try:
        port = parts.port
    except ValueError:
        return ""
    netloc = host if not port else f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parts.path or "/").rstrip("/") or "/"
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.casefold().startswith("utm_") and k.casefold() not in TRACKING_KEYS]
    return urlunsplit(("https" if host else "", netloc, path, urlencode(sorted(query)), ""))


def _tokens(value):
    words = re.findall(r"[a-z0-9]+", str(value or "").casefold())
    return [word for word in words if len(word) > 2 and word not in STOPWORDS]


def _identity_tokens(article):
    title = _tokens(article.get("title"))
    return sorted(set(title))


def _states(article):
    words = set(_tokens(" ".join(str(article.get(k) or "")
                                 for k in ("title", "summary", "feed_summary"))))
    return sorted(name for name, vocabulary in STATE_GROUPS.items() if words & vocabulary)


def material_facts(article):
    text = " ".join(str(article.get(k) or "")
                    for k in ("title", "summary", "feed_summary")).casefold()
    numbers = sorted(set(re.findall(r"(?<![a-z])\d+(?:[.,]\d+)?%?", text)))
    return {"states": _states(article), "numbers": numbers}


def story_fingerprint(article):
    """Content-derived identity, independent of feed IDs and cluster IDs."""
    tokens = _identity_tokens(article)
    if not tokens:
        canonical = normalize_url(article.get("url"))
        tokens = [canonical] if canonical else [str(article.get("id") or "unknown")]
    basis = " ".join(tokens)
    return "story-v1-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]


def annotate(article):
    item = dict(article)
    item["canonical_url"] = normalize_url(item.get("url"))
    item["story_fingerprint"] = story_fingerprint(item)
    item["material_facts"] = material_facts(item)
    return item


def _similarity(left, right):
    a, b = set(_identity_tokens(left)), set(_identity_tokens(right))
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _match(candidate, morning_articles):
    legacy = [item for item in morning_articles
              if (candidate.get("id") and candidate.get("id") == item.get("id"))
              or (candidate.get("cluster_id") and
                  candidate.get("cluster_id") == item.get("cluster_id"))]
    if legacy:
        return legacy[0], 1.0, "legacy_id"
    exact = [item for item in morning_articles
             if candidate["story_fingerprint"] == item.get("story_fingerprint")]
    if exact:
        return exact[0], 1.0, "fingerprint"
    if candidate.get("canonical_url"):
        same_url = [item for item in morning_articles
                    if candidate["canonical_url"] == item.get("canonical_url")]
        if same_url:
            return same_url[0], 1.0, "canonical_url"
    scored = sorted(((_similarity(candidate, item), item) for item in morning_articles),
                    key=lambda pair: pair[0], reverse=True)
    if scored and scored[0][0] >= 0.65:
        return scored[0][1], scored[0][0], "title_overlap"
    return None, 0.0, None


def classify(candidate, morning_articles):
    """Return annotated candidate with new/unchanged/material-update evidence."""
    item = annotate(candidate)
    morning = [annotate(value) if not value.get("story_fingerprint") else value
               for value in morning_articles or []]
    prior, score, method = _match(item, morning)
    if not prior:
        return item | {"change_class": "new_story", "change_reason": "no_morning_match"}

    before = prior.get("material_facts") or material_facts(prior)
    after = item["material_facts"]
    before_states, after_states = set(before.get("states", [])), set(after.get("states", []))
    reason = None
    if "correction" in after_states and "correction" not in before_states:
        reason = "correction_published"
    elif "rumor" in before_states and "confirmed" in after_states:
        reason = "status_confirmed"
    elif set(after.get("numbers", [])) - set(before.get("numbers", [])):
        reason = "new_numeric_fact"

    common = {
        "afternoon_update_of": prior.get("story_fingerprint"),
        "morning_article_id": prior.get("id"),
        "match_method": method,
        "match_score": round(score, 3),
    }
    if reason:
        return item | common | {"change_class": "material_update", "change_reason": reason}
    return item | common | {"change_class": "unchanged", "change_reason": "no_material_fact_change"}


def classify_afternoon(candidates, morning_articles):
    classified = [classify(item, morning_articles) for item in candidates or []]
    included = [item for item in classified if item["change_class"] != "unchanged"]
    rejected = [{"id": item.get("id"), "code": "unchanged_since_morning",
                 "morning_article_id": item.get("morning_article_id")}
                for item in classified if item["change_class"] == "unchanged"]
    return included, {"classified": len(classified), "material_updates": sum(
        item["change_class"] == "material_update" for item in classified),
        "new_stories": sum(item["change_class"] == "new_story" for item in classified),
        "unchanged_rejected": len(rejected), "rejected": rejected}
