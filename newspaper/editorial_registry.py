"""Compile Notion source rows into an auditable local editorial registry."""

import hashlib
import json
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone

SCHEMA_VERSION = 1
ADAPTER_TYPES = {"rss", "connector"}
ADAPTER_STATUSES = {"active", "planned", "blocked"}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _rich_text(prop):
    if not isinstance(prop, dict):
        return ""
    values = prop.get("title") if prop.get("type") == "title" else prop.get("rich_text")
    if not isinstance(values, list):
        return ""
    return "".join(str(value.get("plain_text") or "")
                   for value in values if isinstance(value, dict)).strip()


def _topics(prop):
    if not isinstance(prop, dict) or not isinstance(prop.get("multi_select"), list):
        return []
    out = []
    for value in prop["multi_select"]:
        name = str(value.get("name") or "").strip() if isinstance(value, dict) else ""
        if name and name not in out:
            out.append(name)
    return out


def notion_page_to_source(page):
    props = page.get("properties") if isinstance(page, dict) else None
    props = props if isinstance(props, dict) else {}
    url_prop = props.get("URL") if isinstance(props.get("URL"), dict) else {}
    return {
        "notion_page_id": str(page.get("id") or "").strip(),
        "source": _rich_text(props.get("Source")),
        "url": str(url_prop.get("url") or "").strip() or None,
        "topics": _topics(props.get("Topic / Page")),
        "what_i_read": _rich_text(props.get("What I read here")) or None,
        "must_include": _rich_text(props.get("Must include")) or None,
        "avoid": _rich_text(props.get("Avoid")) or None,
        "sufficiency": _rich_text(props.get("Sufficiency")) or None,
        "last_edited_time": str(page.get("last_edited_time") or "").strip() or None,
    }


def _normalize_adapter(raw):
    if not isinstance(raw, dict):
        raise ValueError("adapter must be an object")
    adapter_type = str(raw.get("type") or "").strip().lower()
    status = str(raw.get("status") or "active").strip().lower()
    if adapter_type not in ADAPTER_TYPES:
        raise ValueError(f"unknown adapter type: {adapter_type or '(empty)'}")
    if status not in ADAPTER_STATUSES:
        raise ValueError(f"unknown adapter status: {status or '(empty)'}")
    out = {"type": adapter_type, "status": status}
    if adapter_type == "rss":
        url = str(raw.get("url") or "").strip()
        if not url:
            raise ValueError("rss adapter requires url")
        out["url"] = url
    else:
        connector = str(raw.get("connector") or "").strip()
        if not connector:
            raise ValueError("connector adapter requires connector")
        out["connector"] = connector
    if raw.get("note"):
        out["note"] = str(raw["note"]).strip()[:500]
    return out


def _adapter_sources(config):
    if not isinstance(config, dict):
        raise ValueError("adapter configuration must be an object")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"adapter schema_version must be {SCHEMA_VERSION}")
    sources = config.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("adapter configuration requires sources object")
    return sources


def _registry_core(value):
    return {"schema_version": value.get("schema_version"),
            "sources": value.get("sources", [])}


def _fingerprint(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compile_registry(notion_pages, adapter_config, previous=None, generated_at=None):
    generated_at = generated_at or _now_iso()
    configured = _adapter_sources(adapter_config)
    normalized, errors, warnings, seen = [], [], [], {}
    pages = notion_pages if isinstance(notion_pages, list) else []

    for index, page in enumerate(pages):
        record = notion_page_to_source(page)
        identity = record["source"].casefold()
        location = record["notion_page_id"] or f"row-{index + 1}"
        if not record["source"]:
            errors.append({"code": "missing_source", "row": location})
            continue
        if not record["notion_page_id"]:
            errors.append({"code": "missing_page_id", "source": record["source"]})
            continue
        if identity in seen:
            errors.append({"code": "duplicate_source", "source": record["source"],
                           "rows": [seen[identity], location]})
            continue
        seen[identity] = location
        if record["source"].casefold().startswith("tbd"):
            warnings.append({"code": "research_queue", "source": record["source"]})
        if not record["topics"]:
            warnings.append({"code": "missing_topics", "source": record["source"]})
        raw_adapters = configured.get(record["source"], [])
        if not isinstance(raw_adapters, list):
            errors.append({"code": "invalid_adapter_list", "source": record["source"]})
            raw_adapters = []
        adapters = []
        for raw in raw_adapters:
            try:
                adapters.append(_normalize_adapter(raw))
            except ValueError as exc:
                errors.append({"code": "invalid_adapter", "source": record["source"],
                               "detail": str(exc)})
        if not adapters:
            warnings.append({"code": "missing_adapter", "source": record["source"]})
        elif not any(adapter["status"] == "active" for adapter in adapters):
            warnings.append({"code": "no_active_adapter", "source": record["source"]})
        record["adapters"] = adapters
        normalized.append(record)

    normalized.sort(key=lambda item: (item["source"].casefold(), item["notion_page_id"]))
    known = {item["source"] for item in normalized}
    for source in sorted(set(configured) - known, key=str.casefold):
        warnings.append({"code": "orphan_adapter_mapping", "source": source})

    registry = {"schema_version": SCHEMA_VERSION, "generated_at": generated_at,
                "sources": normalized}
    previous_sources = {item.get("source"): item
                        for item in (previous or {}).get("sources", [])
                        if isinstance(item, dict) and item.get("source")}
    current_sources = {item["source"]: item for item in normalized}
    added = sorted(set(current_sources) - set(previous_sources), key=str.casefold)
    removed = sorted(set(previous_sources) - set(current_sources), key=str.casefold)
    changed = sorted((source for source in set(current_sources) & set(previous_sources)
                      if _fingerprint(current_sources[source]) !=
                      _fingerprint(previous_sources[source])), key=str.casefold)
    unchanged = sorted((source for source in set(current_sources) & set(previous_sources)
                        if source not in changed), key=str.casefold)
    active = sum(1 for source in normalized
                 if any(adapter["status"] == "active" for adapter in source["adapters"]))
    report = {
        "schema_version": SCHEMA_VERSION,
        "checked_at": generated_at,
        "success": not errors,
        "registry_changed": _registry_core(registry) != _registry_core(previous or {}),
        "counts": {
            "notion_rows": len(pages), "registry_sources": len(normalized),
            "active_sources": active,
            "planned_or_blocked_sources": sum(
                1 for source in normalized if source["adapters"] and
                not any(adapter["status"] == "active" for adapter in source["adapters"])),
            "missing_adapter_sources": sum(1 for source in normalized if not source["adapters"]),
            "errors": len(errors), "warnings": len(warnings),
        },
        "changes": {"added": added, "changed": changed, "removed": removed,
                    "unchanged": unchanged},
        "errors": errors, "warnings": warnings,
    }
    return registry, report, bool(errors)


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return deepcopy(default)


def atomic_write_json(path, payload):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".registry-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def reconcile_to_files(notion_pages, adapter_config, registry_path, report_path,
                       generated_at=None):
    previous = load_json(registry_path, default={}) or {}
    compiled, report, fatal = compile_registry(
        notion_pages, adapter_config, previous=previous, generated_at=generated_at)
    if not fatal and report["registry_changed"]:
        atomic_write_json(registry_path, compiled)
    elif not fatal and previous:
        compiled = previous
    report["registry_updated"] = bool(not fatal and report["registry_changed"])
    report["last_known_good_preserved"] = bool(fatal and previous)
    atomic_write_json(report_path, report)
    return compiled, report, fatal


def write_failure_report(report_path, registry_path, detail, checked_at=None):
    previous = load_json(registry_path, default={}) or {}
    report = {
        "schema_version": SCHEMA_VERSION, "checked_at": checked_at or _now_iso(),
        "success": False, "registry_changed": False, "registry_updated": False,
        "last_known_good_preserved": bool(previous),
        "counts": {"errors": 1, "warnings": 0},
        "changes": {"added": [], "changed": [], "removed": [], "unchanged": []},
        "errors": [{"code": "notion_query_failed", "detail": str(detail)[:1000]}],
        "warnings": [],
    }
    atomic_write_json(report_path, report)
    return report
