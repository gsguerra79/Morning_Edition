"""Cached Formula 1 race desk built from public structured data.

Championship tables come from the maintained Jolpica/Ergast-compatible API.
Completed-session timing comes from Formula 1's own static timing archive.
When OpenF1 credentials are configured, its authenticated REST API adds a
current-session snapshot; failures never displace the finalized archive data.
"""

import json
import os
import tempfile
import threading
import time
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone


YEAR = datetime.now(timezone.utc).year
JOLPICA = "https://api.jolpi.ca/ergast/f1/current"
F1_ARCHIVE = "https://livetiming.formula1.com/static"
OPENF1_API = "https://api.openf1.org"
CACHE_FILE = os.environ.get("F1_CACHE_FILE", "/data/f1-cache.json")
CACHE_SECONDS = int(os.environ.get("F1_CACHE_SECONDS", "300"))
USER_AGENT = "TheForgeDaily/2.0 (https://github.com/gsguerra79/Morning_Edition)"

_lock = threading.Lock()
_memory = None
_memory_at = 0.0
_openf1_access_token = None
_openf1_token_until = 0.0


def _json(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8-sig"))


def _openf1_enabled():
    return bool(os.environ.get("OPENF1_USERNAME") and os.environ.get("OPENF1_PASSWORD"))


def _openf1_token():
    """Exchange backend-only credentials for a short-lived bearer token."""
    global _openf1_access_token, _openf1_token_until
    now = time.time()
    if _openf1_access_token and now < _openf1_token_until:
        return _openf1_access_token
    body = urllib.parse.urlencode({
        "username": os.environ["OPENF1_USERNAME"],
        "password": os.environ["OPENF1_PASSWORD"],
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{OPENF1_API}/token", data=body,
        headers={"User-Agent": USER_AGENT,
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    token = payload.get("access_token")
    if not token:
        raise ValueError("OpenF1 authentication returned no access token")
    _openf1_access_token = token
    _openf1_token_until = now + max(60, int(payload.get("expires_in") or 3600) - 120)
    return token


def _openf1_json(endpoint, **params):
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{OPENF1_API}/v1/{endpoint}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json",
                 "Authorization": f"Bearer {_openf1_token()}"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _iso(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _lap_time(value):
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return ""
    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)}:{remainder:06.3f}" if minutes else f"{remainder:.3f}"


def _openf1_snapshot(now):
    """Return a compact live/current-session classification, not telemetry."""
    sessions = _openf1_json("sessions", session_key="latest")
    if not sessions:
        return None
    session = sessions[-1]
    start, end = _iso(session.get("date_start")), _iso(session.get("date_end"))
    if not start or not end or not start - timedelta(minutes=30) <= now <= end + timedelta(minutes=30):
        return None
    key = session.get("session_key")
    drivers = _openf1_json("drivers", session_key=key)
    driver_map = {str(item.get("driver_number")): item for item in drivers}
    try:
        final = _openf1_json("session_result", session_key=key)
    except urllib.error.HTTPError as exc:
        # OpenF1 returns 404 until an official classification exists. During a
        # live session that means "not final yet", not provider failure.
        if exc.code != 404:
            raise
        final = []
    provisional = not bool(final)
    raw_rows = final
    if provisional:
        laps = _openf1_json("laps", session_key=key)
        best = {}
        for lap in laps:
            duration = lap.get("lap_duration")
            if not duration:
                continue
            number = str(lap.get("driver_number"))
            if number not in best or float(duration) < float(best[number]["lap_duration"]):
                best[number] = lap
        raw_rows = sorted(best.values(), key=lambda item: float(item["lap_duration"]))
        for position, item in enumerate(raw_rows, 1):
            item = dict(item)
            item["position"] = position
            raw_rows[position - 1] = item
    rows = []
    leader = None
    for item in sorted(raw_rows, key=lambda row: int(row.get("position") or 999)):
        number = str(item.get("driver_number"))
        driver = driver_map.get(number) or {}
        duration = item.get("duration") if final else item.get("lap_duration")
        if isinstance(duration, list):
            duration = next((value for value in reversed(duration) if value), None)
        if leader is None and duration:
            leader = float(duration)
        gap = item.get("gap_to_leader")
        if isinstance(gap, list):
            gap = next((value for value in reversed(gap) if value is not None), None)
        if provisional and duration and leader is not None:
            gap = float(duration) - leader
        rows.append({
            "position": int(item.get("position") or len(rows) + 1),
            "number": number,
            "code": driver.get("name_acronym"),
            "name": driver.get("full_name") or driver.get("broadcast_name"),
            "team": driver.get("team_name"),
            "team_colour": driver.get("team_colour"),
            "time": _lap_time(duration),
            "gap": (f"+{float(gap):.3f}" if isinstance(gap, (int, float)) and gap else
                    (str(gap) if gap not in (None, 0) else "")),
            "laps": int(item.get("number_of_laps") or item.get("lap_number") or 0),
            "status": ("DSQ" if item.get("dsq") else "DNF" if item.get("dnf") else
                       "DNS" if item.get("dns") else "provisional" if provisional else "classified"),
        })
    weather_rows = _openf1_json("weather", session_key=key)
    weather = weather_rows[-1] if weather_rows else {}
    return {
        "meeting": session.get("meeting_name"),
        "country": session.get("country_name"),
        "circuit": session.get("circuit_short_name"),
        "session": session.get("session_name"),
        "type": session.get("session_type"),
        "start": start.isoformat(), "end": end.isoformat(),
        "provisional": provisional,
        "weather": {"air_c": weather.get("air_temperature"),
                    "track_c": weather.get("track_temperature"),
                    "rainfall": weather.get("rainfall"),
                    "wind_kph": weather.get("wind_speed")},
        "rows": rows,
        "source": "OpenF1 live data", "source_url": "https://openf1.org/",
    }


def _offset(value):
    raw = str(value or "00:00:00")
    sign = -1 if raw.startswith("-") else 1
    parts = raw.lstrip("+-").split(":")
    try:
        return sign * timedelta(hours=int(parts[0]), minutes=int(parts[1]))
    except (ValueError, IndexError):
        return timedelta(0)


def _utc(session, field):
    value = session.get(field)
    if not value:
        return None
    try:
        local = datetime.fromisoformat(str(value))
        return (local - _offset(session.get("GmtOffset"))).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _standings_rows(payload, kind):
    table = ((payload.get("MRData") or {}).get("StandingsTable") or {})
    lists = table.get("StandingsLists") or []
    block = lists[0] if lists else {}
    key = "DriverStandings" if kind == "drivers" else "ConstructorStandings"
    rows = []
    for item in block.get(key) or []:
        if kind == "drivers":
            driver = item.get("Driver") or {}
            constructors = item.get("Constructors") or []
            rows.append({
                "position": int(item.get("position") or 0),
                "code": driver.get("code"),
                "name": " ".join(filter(None, [driver.get("givenName"), driver.get("familyName")])),
                "team": (constructors[0].get("name") if constructors else None),
                "points": float(item.get("points") or 0),
                "wins": int(item.get("wins") or 0),
            })
        else:
            constructor = item.get("Constructor") or {}
            rows.append({
                "position": int(item.get("position") or 0),
                "name": constructor.get("name"),
                "points": float(item.get("points") or 0),
                "wins": int(item.get("wins") or 0),
            })
    return {
        "season": table.get("season"),
        "round": table.get("round"),
        "rows": rows,
    }


def _session_result(session):
    path = str(session.get("Path") or "").strip("/") + "/"
    base = f"{F1_ARCHIVE}/{path}"
    info = _json(base + "SessionInfo.json")
    if str(info.get("SessionStatus") or "").casefold() not in ("finalised", "finished", "ends"):
        return None
    timing = _json(base + "TimingData.json")
    drivers = _json(base + "DriverList.json")
    try:
        weather = _json(base + "WeatherData.json")
    except Exception:
        weather = {}
    rows = []
    for number, line in (timing.get("Lines") or {}).items():
        driver = drivers.get(str(number)) or drivers.get(str(line.get("RacingNumber"))) or {}
        best = line.get("BestLapTime") or {}
        gap = (line.get("GapToLeader") or line.get("TimeDiffToFastest") or "")
        rows.append({
            "position": int(line.get("Position") or line.get("Line") or 999),
            "number": str(line.get("RacingNumber") or number),
            "code": driver.get("Tla"),
            "name": driver.get("FullName") or driver.get("BroadcastName"),
            "team": driver.get("TeamName"),
            "team_colour": driver.get("TeamColour"),
            "time": best.get("Value") or line.get("TimeDiffToPositionAhead") or "",
            "gap": gap,
            "laps": int(line.get("NumberOfLaps") or 0),
            "status": "retired" if line.get("Retired") else "classified",
        })
    rows.sort(key=lambda row: row["position"])
    meeting = info.get("Meeting") or {}
    return {
        "meeting": meeting.get("Name"),
        "official_name": meeting.get("OfficialName"),
        "country": (meeting.get("Country") or {}).get("Name"),
        "circuit": (meeting.get("Circuit") or {}).get("ShortName"),
        "session": info.get("Name") or session.get("Name"),
        "type": info.get("Type") or session.get("Type"),
        "start": (_utc(info, "StartDate") or _utc(session, "StartDate")).isoformat(),
        "end": (_utc(info, "EndDate") or _utc(session, "EndDate")).isoformat(),
        "weather": {
            "air_c": weather.get("AirTemp"), "track_c": weather.get("TrackTemp"),
            "rainfall": weather.get("Rainfall"), "wind_kph": weather.get("WindSpeed"),
        },
        "rows": rows,
        "source": "Formula 1 timing archive",
        "source_url": base + "Index.json",
    }


def _race_weekend(index, now):
    active = None
    for meeting in index.get("Meetings") or []:
        sessions = meeting.get("Sessions") or []
        starts = [_utc(item, "StartDate") for item in sessions]
        ends = [_utc(item, "EndDate") for item in sessions]
        starts = [item for item in starts if item]
        ends = [item for item in ends if item]
        if starts and ends and min(starts) - timedelta(hours=18) <= now <= max(ends) + timedelta(hours=18):
            active = meeting
            break
    if not active:
        return None
    sessions = active.get("Sessions") or []
    completed = [item for item in sessions
                 if item.get("Path") and _utc(item, "EndDate") and _utc(item, "EndDate") <= now]
    result = None
    for session in sorted(completed, key=lambda item: _utc(item, "EndDate"), reverse=True):
        try:
            result = _session_result(session)
        except Exception:
            continue
        if result and result.get("rows"):
            break
    future = [item for item in sessions if _utc(item, "StartDate") and _utc(item, "StartDate") > now]
    next_session = min(future, key=lambda item: _utc(item, "StartDate")) if future else None
    live = [item for item in sessions if _utc(item, "StartDate") and _utc(item, "EndDate")
            and _utc(item, "StartDate") <= now <= _utc(item, "EndDate")]
    current_session = live[0] if live else None
    return {
        "active": True,
        "meeting": active.get("Name"),
        "country": (active.get("Country") or {}).get("Name"),
        "circuit": (active.get("Circuit") or {}).get("ShortName"),
        "latest_session": result,
        "current_session": ({
            "name": current_session.get("Name"),
            "type": current_session.get("Type"),
            "start": _utc(current_session, "StartDate").isoformat(),
            "end": _utc(current_session, "EndDate").isoformat(),
        } if current_session else None),
        "next_session": ({
            "name": next_session.get("Name"),
            "type": next_session.get("Type"),
            "start": _utc(next_session, "StartDate").isoformat(),
            "end": _utc(next_session, "EndDate").isoformat(),
        } if next_session else None),
    }


def _build(now=None):
    now = now or datetime.now(timezone.utc)
    drivers = _standings_rows(_json(f"{JOLPICA}/driverstandings/"), "drivers")
    teams = _standings_rows(_json(f"{JOLPICA}/constructorstandings/"), "teams")
    index = _json(f"{F1_ARCHIVE}/{now.year}/Index.json")
    weekend = _race_weekend(index, now)
    errors = []
    if weekend and _openf1_enabled():
        try:
            weekend["live_session"] = _openf1_snapshot(now)
        except Exception as exc:
            errors.append(f"OpenF1: {exc}")
    return {
        "updated_at": now.isoformat(),
        "stale": False,
        "standings": {"drivers": drivers, "teams": teams,
                      "source": "Jolpica F1", "source_url": "https://jolpi.ca/"},
        "race_weekend": weekend,
        "openf1_enabled": _openf1_enabled(),
        "errors": errors,
    }


def _load_file():
    try:
        with open(CACHE_FILE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def _save_file(payload):
    directory = os.path.dirname(CACHE_FILE) or "."
    os.makedirs(directory, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix=".f1-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(path, CACHE_FILE)
    except Exception:
        try:
            os.unlink(path)
        except OSError:
            pass
        raise


def get_f1(force=False):
    global _memory, _memory_at
    with _lock:
        now = time.time()
        if not force and _memory and now - _memory_at < CACHE_SECONDS:
            return _memory
        cached = _load_file()
        if not force and cached:
            try:
                age = now - datetime.fromisoformat(cached["updated_at"]).timestamp()
            except (KeyError, TypeError, ValueError):
                age = CACHE_SECONDS + 1
            if age < CACHE_SECONDS:
                _memory, _memory_at = cached, now
                return cached
        try:
            payload = _build()
            _save_file(payload)
        except Exception as exc:
            if not cached:
                raise
            payload = dict(cached)
            payload["stale"] = True
            payload["errors"] = list(payload.get("errors") or []) + [str(exc)]
        _memory, _memory_at = payload, now
        return payload
