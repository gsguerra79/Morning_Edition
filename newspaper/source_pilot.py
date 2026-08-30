"""Repeatable RSS pilot observations with durable, bounded evidence."""
import re
import urllib.request
from datetime import datetime, timedelta, timezone

from pipeline import parse_feed

PROMOTIONAL = re.compile(r"\b(deal|sale|discount|coupon|sponsored|buy now|gift guide)\b", re.I)


def fetch(url, timeout=20):
    request = urllib.request.Request(url, headers={"User-Agent": "MorningEditionPilot/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def observe(source, body, now=None, lookback_days=14):
    now = now or datetime.now(timezone.utc)
    items = parse_feed(body, source["source"], source["page"], now - timedelta(days=lookback_days))
    urls = {item.get("url") for item in items if item.get("url")}
    promo = sum(bool(PROMOTIONAL.search(" ".join((item.get("title", ""), item.get("feed_summary", ""))))) for item in items)
    return {"source": source["source"], "page": source["page"], "ok": True,
            "items": len(items), "unique_urls": len(urls), "promotional": promo,
            "sample_titles": [item.get("title") for item in items[:5]]}


def record(state, observations, observed_at, minimum_hours=48):
    state = dict(state or {})
    runs = list(state.get("runs") or [])
    runs.append({"observed_at": observed_at, "sources": observations})
    state.update(schema_version=1, runs=runs[-40:])
    state.setdefault("started_at", observed_at)
    hours = max(0, (datetime.fromisoformat(observed_at) - datetime.fromisoformat(state["started_at"])).total_seconds() / 3600)
    summaries = {}
    names = sorted({item["source"] for run in state["runs"] for item in run["sources"]})
    for name in names:
        rows = [item for run in state["runs"] for item in run["sources"] if item["source"] == name]
        good = [item for item in rows if item.get("ok")]
        total = sum(item.get("items", 0) for item in good)
        promo = sum(item.get("promotional", 0) for item in good)
        summaries[name] = {"runs": len(rows), "successful_runs": len(good),
                           "success_rate": round(len(good) / len(rows), 3),
                           "items_observed": total,
                           "promotional_ratio": round(promo / total, 3) if total else 0,
                           "window_hours": round(hours, 2),
                           "eligible_for_verdict": hours >= minimum_hours}
    state["summary"] = summaries
    return state


def run(config, state=None, now=None, fetcher=fetch):
    now = now or datetime.now(timezone.utc)
    observations = []
    for source in config["sources"]:
        try:
            observations.append(observe(source, fetcher(source["url"]), now,
                                        config.get("lookback_days", 14)))
        except Exception as exc:
            observations.append({"source": source["source"], "page": source["page"], "ok": False,
                                 "items": 0, "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
    return record(state, observations, now.isoformat(), config.get("minimum_observation_hours", 48))
