"""Canonical payloads for desks that remain current between editions.

The newspaper edition is immutable, but Formula 1 and Comics have explicit
live contracts.  This module gives Home and the dedicated pages one shared
truth, including a stable six-story F1 front-page subset.
"""
import json
import os
import re
import tempfile
import threading
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha1
from html import unescape
from urllib.parse import urljoin


STATE_FILE = os.environ.get('LIVE_DESKS_FILE', '/data/live-desks.json')
F1_FRONT_SIZE = 6
F1_NORMAL_REPLACEMENTS = 2
SCHEMA_VERSION = 4
COMIC_REFRESH_SECONDS = 15 * 60
_lock = threading.Lock()
COMIC_FEEDS = (
    ('GiantITP', 'https://www.giantitp.com/comics/oots.rss'),
    ('Wilde Life', 'https://www.wildelifecomic.com/comic/rss'),
)


def _atomic_write(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.live-desks-', suffix='.json',
                               dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _load(path):
    try:
        with open(path, encoding='utf-8') as fh:
            value = json.load(fh)
            return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _f1_tier(article):
    """Match the reader's strict Race Desk admission rules."""
    title = str(article.get('title') or '').lower()
    text = f"{article.get('title') or ''} {article.get('summary') or ''}".lower()
    if re.search(r'\b(rumou?r|speculat|could join|linked with|tipped for|may replace)\b', text):
        return 'paddock'
    if re.search(r'\b(wedding|girlfriend|boyfriend|family|lifestyle|holiday|vacation|social media|off.track|personal life|health|injur|recovery|recovers)\b', text):
        return 'paddock'
    if re.search(r'\b(strategy|strategic|undercut|overcut|pit stop|tyre choice|tire choice|degradation|race pace|long run|fuel load|stint)\b', text):
        return 'desk'
    if re.search(r'\b(appointed|appointment|signing|signed|confirmed|team principal|driver line.up|personnel|replacement)\b', text):
        return 'desk'
    if re.search(r'\b(technical|technology|upgrade|engine|power unit|aero|regulation|rule|tyre|tire|battery|chassis|floor|wing|design|top speed|mj)\b', title):
        return 'desk'
    if re.search(r'\b(fp[123]|practice(?:\s+[123])?|qualifying|sprint(?:\s+(?:race|shootout|qualifying))?|race (?:result|report)|live timing|as it happened|leads?\b|outpaces?\b|tops?\b|fastest\b)\b', title):
        return 'desk'
    if re.search(r'\b(penalt(?:y|ies)|investigation|crash|incident|red flag|withdraws?|disqualif|official decision)\b', title):
        return 'desk'
    return 'paddock'


def _f1_target(items):
    """Mirror the balanced six-story Home selection used by the reader."""
    desk = [article for article in items if _f1_tier(article) == 'desk']
    ranked = desk + [article for article in items if _f1_tier(article) != 'desk']
    # Six qualifying Race Desk pieces means no Paddock item belongs on Home.
    items = desk if len(desk) >= F1_FRONT_SIZE else ranked
    chosen, ids, sources = [], set(), {}

    def add_kind(kind):
        item = next((article for article in items
                     if article.get('id') not in ids
                     and article.get('f1_kind') == kind
                     and sources.get(article.get('source'), 0) < 2), None)
        if not item:
            return
        ids.add(item.get('id'))
        chosen.append(item)
        source = item.get('source')
        sources[source] = sources.get(source, 0) + 1

    for kind in ('results_updates', 'results_updates', 'technical',
                 'preview_forecast', 'news'):
        add_kind(kind)
    for item in items:
        if len(chosen) >= F1_FRONT_SIZE:
            break
        if item.get('id') in ids or sources.get(item.get('source'), 0) >= 2:
            continue
        if (item.get('f1_kind') == 'rumor_interview'
                and any(a.get('f1_kind') == 'rumor_interview' for a in chosen)):
            continue
        ids.add(item.get('id'))
        chosen.append(item)
        source = item.get('source')
        sources[source] = sources.get(source, 0) + 1
    for item in items:
        if len(chosen) >= F1_FRONT_SIZE:
            break
        if item.get('id') not in ids:
            ids.add(item.get('id'))
            chosen.append(item)
    return chosen[:F1_FRONT_SIZE]


def _urgent(article):
    """Session/result developments may displace Home cards immediately."""
    return article.get('f1_kind') == 'results_updates'


def _stable_front(items, previous_ids):
    target = _f1_target(items)
    if not previous_ids:
        return [a.get('id') for a in target]

    available = {a.get('id'): a for a in items}
    target_ids = [a.get('id') for a in target]
    kept = [item_id for item_id in previous_ids if item_id in available]

    # Completed-session and other results updates are allowed through
    # immediately. Ordinary editorial churn is capped at two cards per ingest.
    urgent_ids = [item_id for item_id in target_ids
                  if item_id not in kept and _urgent(available[item_id])]
    normal_ids = [item_id for item_id in target_ids
                  if item_id not in kept and item_id not in urgent_ids]
    desired = urgent_ids + normal_ids[:F1_NORMAL_REPLACEMENTS]

    for item_id in desired:
        if item_id in kept:
            continue
        if len(kept) >= F1_FRONT_SIZE:
            removable = next((old for old in reversed(kept)
                              if old not in target_ids or not _urgent(available[old])),
                             kept[-1])
            kept.remove(removable)
        kept.append(item_id)

    # Missing old stories must be backfilled even when the normal churn budget
    # has been consumed, otherwise Home would show fewer than six.
    for item_id in target_ids:
        if len(kept) >= F1_FRONT_SIZE:
            break
        if item_id not in kept:
            kept.append(item_id)

    # Present the stable set in current editorial order.
    order = {article.get('id'): index for index, article in enumerate(items)}
    return sorted(kept[:F1_FRONT_SIZE], key=lambda item_id: order.get(item_id, 9999))


def _latest_comics(articles):
    latest = {}
    for article in articles:
        if article.get('category') != 'comics':
            continue
        source = str(article.get('source') or '').casefold()
        key = ('giantitp' if 'giantitp' in source or 'order of the stick' in source
               else 'wilde-life' if 'wilde life' in source else source)
        if not key:
            continue
        current = latest.get(key)
        if not current or str(article.get('published_at') or '') > str(current.get('published_at') or ''):
            latest[key] = article
    return [latest[key] for key in ('giantitp', 'wilde-life') if key in latest]


def _fetch(url, timeout=10):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'The Forge Daily/1.0 (comic subscription reader)',
        'Accept': 'application/rss+xml, application/xml, text/html;q=0.9,*/*;q=0.8',
    })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode('utf-8', 'replace')


def _comic_page_image(source, url):
    markup = _fetch(url)
    if source == 'GiantITP':
        match = re.search(r'<img[^>]+src=["\']([^"\']*/comics/oots/[^"\']+)["\']',
                          markup, re.I)
    else:
        match = (re.search(r'<img(?=[^>]+\bid=["\']cc-comic["\'])[^>]+src=["\']([^"\']+)["\']', markup, re.I)
                 or re.search(r'<img(?=[^>]+\bsrc=["\']([^"\']+)["\'])[^>]+\bid=["\']cc-comic["\']', markup, re.I))
    return urljoin(url, unescape(match.group(1))) if match else None


def _fetch_current_comics(fallback, generated_at):
    """Read each subscription directly; issue ranking must not age comics."""
    found = []
    fallback_by_source = {str(a.get('source') or '').casefold(): a for a in fallback}
    for source, feed_url in COMIC_FEEDS:
        try:
            root = ET.fromstring(_fetch(feed_url))
            item = root.find('./channel/item')
            if item is None:
                raise ValueError('empty comic feed')
            title = (item.findtext('title') or '').strip()
            url = (item.findtext('link') or '').strip()
            if not title or not url:
                raise ValueError('comic item lacks title or link')
            published = generated_at
            if item.findtext('pubDate'):
                published = parsedate_to_datetime(item.findtext('pubDate')).isoformat()
            description = item.findtext('description') or ''
            thumb_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description, re.I)
            image = urljoin(url, unescape(thumb_match.group(1))) if thumb_match else None
            try:
                image = _comic_page_image(source, url) or image
            except Exception:
                # A current feed item must never roll back merely because its
                # full-size artwork endpoint is temporarily slow.
                pass
            found.append({
                'id': sha1(url.encode('utf-8')).hexdigest()[:8],
                'cluster_id': sha1(url.encode('utf-8')).hexdigest()[:8],
                'cluster_rep': True,
                'title': title, 'url': url, 'source': source,
                'category': 'comics', 'published_at': published,
                'image': image,
                'summary': '', 'score': 10, 'selection_score': 10,
                'subscription_current': True,
            })
        except Exception:
            aliases = ('giantitp', 'the order of the stick') if source == 'GiantITP' else ('wilde life',)
            old = next((article for name, article in fallback_by_source.items()
                        if any(alias in name for alias in aliases)), None)
            if old:
                found.append(old)
    return found


def build(digest, path=None, fetch_current_comics=False):
    """Return and persist the canonical current live-desk payload."""
    path = path or STATE_FILE
    generated_at = digest.get('generated_at') or digest.get('published_at')
    articles = list(digest.get('articles') or [])
    f1_articles = [a for a in articles if a.get('category') == 'formula1']
    comics = _latest_comics(articles)

    with _lock:
        previous = _load(path)
        cached_comics = ((previous.get('desks') or {}).get('comics') or {}).get('articles') or []
        checked = previous.get('comics_checked_at')
        try:
            checked_at = datetime.fromisoformat(checked)
            comics_fresh = datetime.now(timezone.utc) - checked_at < timedelta(seconds=COMIC_REFRESH_SECONDS)
        except (TypeError, ValueError):
            comics_fresh = False
        cache_current = len(cached_comics) == 2 and all(a.get('subscription_current') for a in cached_comics)
        same_digest = (previous.get('schema_version') == SCHEMA_VERSION
                       and previous.get('source_generated_at') == generated_at)
        if same_digest and (not fetch_current_comics or (cache_current and comics_fresh)):
            return previous
        if fetch_current_comics:
            comics = _fetch_current_comics(comics, generated_at)
        previous_ids = ((previous.get('desks') or {}).get('formula1') or {}).get('front_page_ids') or []
        payload = {
            'schema_version': SCHEMA_VERSION,
            'source_generated_at': generated_at,
            'comics_checked_at': datetime.now(timezone.utc).isoformat() if fetch_current_comics else checked,
            'desks': {
                'formula1': {
                    'mode': 'live', 'updated_at': generated_at,
                    'articles': f1_articles,
                    'front_page_ids': _stable_front(f1_articles, previous_ids),
                },
                'comics': {
                    'mode': 'always_current', 'updated_at': generated_at,
                    'articles': comics,
                    'front_page_ids': [a.get('id') for a in comics],
                },
            },
        }
        _atomic_write(path, payload)
        return payload
