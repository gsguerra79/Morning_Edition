"""Cached first-party weather desk for Houston with a compact Rio observation."""

import html
import json
import os
import re
import tempfile
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


HOUSTON_LAT = 29.7604
HOUSTON_LON = -95.3698
RIO_LAT = -22.9068
RIO_LON = -43.1729
CACHE_FILE = os.environ.get("WEATHER_CACHE_FILE", "/data/weather-cache.json")
CACHE_SECONDS = int(os.environ.get("WEATHER_CACHE_SECONDS", "900"))
USER_AGENT = "TheForgeDaily/1.0 (https://github.com/gsguerra79/Morning_Edition)"
RADAR_IMAGE = "https://radar.weather.gov/ridge/standard/KHGX_loop.gif"
RADAR_PAGE = "https://radar.weather.gov/station/KHGX/standard"
WEATHER_TERMS = re.compile(
    r"\b(storm|thunder|flood|hurricane|tropical|cyclone|tornado|warning|watch|"
    r"advisory|alert|surge|heavy rain|severe weather|lightning)\b", re.I)

_lock = threading.Lock()
_memory = None
_memory_at = 0.0


def _request(url, accept="application/geo+json, application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urllib.request.urlopen(req, timeout=12) as response:
        return response.read()


def _json(url):
    return json.loads(_request(url).decode("utf-8"))


def _text(value):
    value = re.sub(r"<[^>]+>", " ", html.unescape(str(value or "")))
    return re.sub(r"\s+", " ", value).strip()


def _celsius(value, unit="F"):
    if value is None:
        return None
    number = float(value)
    return round((number - 32) * 5 / 9, 1) if str(unit or "F").upper() == "F" else round(number, 1)


def _rss(url, source, limit=8):
    root = ET.fromstring(_request(url, "application/rss+xml, application/xml, text/xml"))
    rows = []
    for item in root.findall(".//item"):
        title = _text(item.findtext("title"))
        summary = _text(item.findtext("description"))
        link = _text(item.findtext("link"))
        if not title or not link or not WEATHER_TERMS.search(f"{title} {summary}"):
            continue
        rows.append({
            "title": title,
            "summary": summary[:320],
            "url": link,
            "source": source,
            "published_at": _text(item.findtext("pubDate")),
            "kind": "article",
        })
        if len(rows) >= limit:
            break
    return rows


def _weekly(periods):
    days = {}
    order = []
    for period in periods:
        start = str(period.get("startTime") or "")
        date = start[:10]
        if not date:
            continue
        if date not in days:
            days[date] = {"date": date, "name": period.get("name"), "high": None,
                          "low": None, "forecast": None, "precipitation": 0,
                          "icon": period.get("icon")}
            order.append(date)
        day = days[date]
        temp = _celsius(period.get("temperature"), period.get("temperatureUnit"))
        if period.get("isDaytime"):
            day["high"] = temp
            day["forecast"] = period.get("shortForecast")
            day["icon"] = period.get("icon") or day["icon"]
        else:
            day["low"] = temp
            day["forecast"] = day["forecast"] or period.get("shortForecast")
        chance = (period.get("probabilityOfPrecipitation") or {}).get("value") or 0
        day["precipitation"] = max(day["precipitation"], chance)
    return [days[date] for date in order[:7]]


def _hourly(periods):
    return [{
        "start": period.get("startTime"),
        "temperature": _celsius(period.get("temperature"), period.get("temperatureUnit")),
        "unit": "C",
        "forecast": period.get("shortForecast"),
        "precipitation": (period.get("probabilityOfPrecipitation") or {}).get("value") or 0,
        "wind": f"{period.get('windSpeed') or ''} {period.get('windDirection') or ''}".strip(),
        "icon": period.get("icon"),
    } for period in periods[:24]]


WMO = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Freezing fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Rain showers", 82: "Heavy showers", 95: "Thunderstorms",
    96: "Thunderstorms with hail", 99: "Severe thunderstorms with hail",
}


def _rio():
    url = ("https://api.open-meteo.com/v1/forecast?latitude=-22.9068&longitude=-43.1729"
           "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
           "precipitation,weather_code,wind_speed_10m"
           "&wind_speed_unit=mph&timezone=America%2FSao_Paulo")
    raw = _json(url)
    current = raw.get("current") or {}
    return {
        "observed_at": current.get("time"),
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "wind_mph": current.get("wind_speed_10m"),
        "condition": WMO.get(current.get("weather_code"), "Current conditions"),
        "source": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
    }


def _build():
    errors = []
    points = _json(f"https://api.weather.gov/points/{HOUSTON_LAT},{HOUSTON_LON}")
    properties = points.get("properties") or {}
    forecast = _json(properties["forecast"])
    hourly = _json(properties["forecastHourly"])
    alerts = _json(f"https://api.weather.gov/alerts/active?point={HOUSTON_LAT},{HOUSTON_LON}")

    alert_cards = []
    for feature in (alerts.get("features") or [])[:5]:
        item = feature.get("properties") or {}
        alert_cards.append({
            "title": item.get("headline") or item.get("event") or "Weather alert",
            "summary": _text(item.get("description"))[:400],
            "url": item.get("@id") or feature.get("id") or "https://www.weather.gov/hgx/",
            "source": "National Weather Service",
            "published_at": item.get("sent"),
            "severity": item.get("severity"),
            "expires": item.get("expires"),
            "kind": "alert",
        })

    articles = list(alert_cards)
    feeds = [
        ("https://www.weather.gov/rss_page.php?site_name=hgx", "NWS Houston/Galveston"),
        ("https://www.nhc.noaa.gov/index-at.xml", "National Hurricane Center"),
    ]
    for url, source in feeds:
        try:
            articles.extend(_rss(url, source))
        except Exception as exc:
            errors.append(f"{source}: {exc}")
    unique, seen = [], set()
    for article in articles:
        key = re.sub(r"\W+", "", article["title"].casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
        if len(unique) >= 6:
            break

    try:
        rio = _rio()
    except Exception as exc:
        rio = None
        errors.append(f"Rio: {exc}")

    hourly_periods = (hourly.get("properties") or {}).get("periods") or []
    forecast_periods = (forecast.get("properties") or {}).get("periods") or []
    current = _hourly(hourly_periods[:1])
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "units": "metric",
        "stale": False,
        "houston": {
            "current": current[0] if current else None,
            "weekly": _weekly(forecast_periods),
            "hourly": _hourly(hourly_periods),
            "alerts": alert_cards,
            "radar": {"image_url": RADAR_IMAGE, "page_url": RADAR_PAGE,
                      "station": "KHGX — Houston/Galveston"},
            "source": "National Weather Service",
            "source_url": "https://www.weather.gov/hgx/",
        },
        "rio": rio,
        "articles": unique,
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
    fd, path = tempfile.mkstemp(prefix=".weather-", suffix=".json", dir=directory)
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


def get_weather(force=False):
    global _memory, _memory_at
    with _lock:
        now = time.time()
        if not force and _memory and now - _memory_at < CACHE_SECONDS:
            return _memory
        cached = _load_file()
        if cached and cached.get("units") != "metric":
            cached = None
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
