"""Read approved, already-open Arc tabs without navigating or creating tabs."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Callable


ALLOWED_HOSTS = {
    "medium.com": "medium",
    "www.ft.com": "financial-times",
}


@dataclass(frozen=True)
class ArcTab:
    source: str
    title: str
    url: str
    text: str
    content_error: str | None = None


def _inventory_script() -> str:
    return '''
tell application "Arc"
  set rows to {}
  repeat with w in windows
    repeat with t in tabs of w
      set u to URL of t
      if u starts with "https://medium.com/" or u starts with "https://www.ft.com/" then
        set end of rows to (id of t) & "|||" & (title of t) & "|||" & u
      end if
    end repeat
  end repeat
  set AppleScript's text item delimiters to linefeed
  return rows as text
end tell
'''.strip()


def _content_script(tab_id: str) -> str:
    safe_id = tab_id.replace('"', '')
    javascript = (
        "JSON.stringify({title:document.title,url:location.href,"
        "text:(document.body?.innerText||'').slice(0,200000)})"
    )
    return f'''
tell application "Arc"
  repeat with w in windows
    repeat with t in tabs of w
      if id of t is "{safe_id}" then return execute t javascript "{javascript}"
    end repeat
  end repeat
end tell
'''.strip()


def _default_runner(host: str, script: str, timeout: int = 10) -> str:
    completed = subprocess.run(
        ["ssh", host, "osascript"], input=script, text=True,
        capture_output=True, check=True, timeout=timeout,
    )
    return completed.stdout


def _source_for_url(url: str) -> str | None:
    from urllib.parse import urlparse
    try:
        return ALLOWED_HOSTS.get((urlparse(url).hostname or "").lower())
    except ValueError:
        return None


def read_tabs(host: str = "mac-studio",
              runner: Callable[..., str] = _default_runner) -> list[ArcTab]:
    tabs: list[ArcTab] = []
    for line in runner(host, _inventory_script()).splitlines():
        if not line.strip():
            continue
        parts = line.split("|||", 2)
        if len(parts) != 3:
            continue
        tab_id, title, url = parts
        source = _source_for_url(url)
        if source is None:
            continue
        text = ""
        content_error = None
        try:
            raw = runner(host, _content_script(tab_id), 5)
            payload = json.loads(raw) if raw.strip() else {}
            title = str(payload.get("title") or title).strip()
            url = str(payload.get("url") or url)
            text = str(payload.get("text") or "")
            if not text.strip():
                content_error = "empty_content"
        except subprocess.TimeoutExpired:
            content_error = "content_timeout"
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip()
            content_error = f"content_command_failed: {detail}" if detail else "content_command_failed"
        except json.JSONDecodeError:
            content_error = "invalid_content_json"
        tabs.append(ArcTab(
            source=source,
            title=title.strip(),
            url=url,
            text=text,
            content_error=content_error,
        ))
    return tabs


def health(tabs: list[ArcTab]) -> dict:
    present = {tab.source for tab in tabs}
    readable = {tab.source for tab in tabs if tab.text.strip()}
    required = set(ALLOWED_HOSTS.values())
    return {
        "status": "ready" if required <= readable else "partial",
        "sources": sorted(present),
        "readable": sorted(readable),
        "missing": sorted(required - present),
        "unreadable": sorted(present - readable),
        "tab_count": len(tabs),
    }
