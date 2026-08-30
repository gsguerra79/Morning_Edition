"""Immutable morning/afternoon newspaper editions."""
import json
import os
import re
import tempfile
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

EDITIONS_DIR = os.environ.get('EDITIONS_DIR', '/data/editions')
TIMEZONE = os.environ.get('TZ', 'America/Chicago')


def _atomic(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.edition-', suffix='.json', dir=os.path.dirname(path))
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, path)


def edition_id(kind, now=None):
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    return f'{now:%Y-%m-%d}-{kind}'


def publish(digest, kind, now=None, force=False):
    if kind not in ('morning', 'afternoon'):
        raise ValueError('kind must be morning or afternoon')
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    eid = edition_id(kind, now)
    path = os.path.join(EDITIONS_DIR, eid + '.json')
    if os.path.exists(path) and not force:
        return load(eid)
    articles = list(digest.get('articles') or [])
    if kind == 'afternoon':
        morning = load(edition_id('morning', now)) or {}
        morning_ids = {a.get('id') for a in morning.get('articles', [])}
        morning_clusters = {a.get('cluster_id') for a in morning.get('articles', [])}
        articles = [a for a in articles if a.get('id') not in morning_ids
                    and a.get('cluster_id') not in morning_clusters]
    for article in articles:
        article.setdefault('why_selected', _why(article))
    payload = {
        'id': eid, 'kind': kind, 'date': now.date().isoformat(),
        'published_at': now.isoformat(), 'article_count': len(articles),
        'articles': articles,
    }
    _atomic(path, payload)
    return payload


def _why(article):
    category = str(article.get('category') or 'your interests').replace('-', ' ')
    n = int(article.get('cluster_size') or 1)
    if n > 1:
        return f'Selected for {category}; confirmed by {n} independent reports.'
    return f'Selected as timely coverage of {category}.'


def load(eid):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-(morning|afternoon)', eid or ''):
        return None
    try:
        with open(os.path.join(EDITIONS_DIR, eid + '.json'), encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def latest():
    items = list_editions()
    return load(items[0]['id']) if items else None


def list_editions():
    try:
        names = sorted((n[:-5] for n in os.listdir(EDITIONS_DIR)
                        if re.fullmatch(r'\d{4}-\d{2}-\d{2}-(morning|afternoon)\.json', n)),
                       reverse=True)
    except OSError:
        return []
    out = []
    for eid in names:
        item = load(eid)
        if item:
            out.append({k: item.get(k) for k in ('id', 'kind', 'date', 'published_at', 'article_count')})
    out.sort(key=lambda item: item.get('published_at') or '', reverse=True)
    # Morning and afternoon may share the same timestamp during first boot;
    # afternoon is still the later issue in the editorial sequence.
    out.sort(key=lambda item: (item.get('date') or '', item.get('kind') == 'afternoon'), reverse=True)
    return out


def maybe_publish(digest, now=None):
    """Publish once after each configured deadline (07:30 and 16:30 local)."""
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    morning_minute = int(os.environ.get('MORNING_MINUTE', '450'))
    afternoon_minute = int(os.environ.get('AFTERNOON_MINUTE', '990'))
    minute = now.hour * 60 + now.minute
    if minute >= afternoon_minute:
        publish(digest, 'morning', now)
        return publish(digest, 'afternoon', now)
    if minute >= morning_minute:
        return publish(digest, 'morning', now)
    return None


def start_background(digest_file):
    """Check publication deadlines independently of the ingestion cadence."""
    def loop():
        while True:
            try:
                with open(digest_file, encoding='utf-8') as fh:
                    maybe_publish(json.load(fh))
            except (OSError, json.JSONDecodeError):
                pass
            threading.Event().wait(30)
    threading.Thread(target=loop, name='edition-publisher', daemon=True).start()
