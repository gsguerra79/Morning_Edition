"""Immutable morning/afternoon newspaper editions."""
import json
import os
import re
import tempfile
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from editorial_selection import select_issue
from story_identity import annotate, classify_afternoon

EDITIONS_DIR = os.environ.get('EDITIONS_DIR', '/data/editions')
TIMEZONE = os.environ.get('TZ', 'America/Chicago')
EDITORIAL_REGISTRY_FILE = os.environ.get('EDITORIAL_REGISTRY_FILE', '/data/editorial-registry.json')
SELECTION_RULES_FILE = os.environ.get('SELECTION_RULES_FILE', '/data/selection-rules.json')


def _atomic(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.edition-', suffix='.json', dir=os.path.dirname(path))
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, path)


def edition_id(kind, now=None):
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    return f'{now:%Y-%m-%d}-{kind}'


def _load_json(path):
    try:
        with open(path, encoding='utf-8') as fh:
            value = json.load(fh)
            return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def publish(digest, kind, now=None, force=False):
    if kind not in ('morning', 'afternoon'):
        raise ValueError('kind must be morning or afternoon')
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    eid = edition_id(kind, now)
    path = os.path.join(EDITIONS_DIR, eid + '.json')
    if os.path.exists(path) and not force:
        return load(eid)
    articles = [annotate(article) for article in (digest.get('articles') or [])]
    candidate_story_index = [{key: article.get(key) for key in (
        'id', 'cluster_id', 'title', 'canonical_url', 'story_fingerprint', 'material_facts')}
        for article in articles if article.get('cluster_rep') is not False]
    change_report = None
    if kind == 'afternoon':
        morning = load(edition_id('morning', now)) or {}
        articles, change_report = classify_afternoon(
            [article for article in articles if article.get('cluster_rep') is not False],
            morning.get('candidate_story_index') or morning.get('articles', []))
    max_stories = int(os.environ.get(
        'MORNING_MAX_STORIES' if kind == 'morning' else 'AFTERNOON_MAX_STORIES',
        '40' if kind == 'morning' else '15'))
    source_share = float(os.environ.get('SOURCE_SHARE_CAP', '0.20'))
    articles, selection_report = select_issue(
        articles,
        registry=_load_json(EDITORIAL_REGISTRY_FILE),
        rules=_load_json(SELECTION_RULES_FILE),
        max_stories=max_stories,
        source_share=source_share,
    )
    if change_report is not None:
        selection_report['material_change'] = change_report
    payload = {
        'id': eid, 'kind': kind, 'date': now.date().isoformat(),
        'published_at': now.isoformat(), 'article_count': len(articles),
        'articles': articles, 'selection_report': selection_report,
    }
    if kind == 'morning':
        payload['candidate_story_index'] = candidate_story_index
    if kind == 'afternoon' and not articles:
        payload['empty_state'] = {
            'code': 'no_material_change',
            'message': 'No new or materially changed stories since the morning edition.',
        }
    _atomic(path, payload)
    return payload


def preview(digest, now=None):
    """Build a bounded current issue without mutating the edition archive."""
    now = now or datetime.now(ZoneInfo(TIMEZONE))
    articles = [annotate(article) for article in (digest.get('articles') or [])]
    max_stories = int(os.environ.get('MORNING_MAX_STORIES', '40'))
    source_share = float(os.environ.get('SOURCE_SHARE_CAP', '0.20'))
    selected, selection_report = select_issue(
        articles,
        registry=_load_json(EDITORIAL_REGISTRY_FILE),
        rules=_load_json(SELECTION_RULES_FILE),
        max_stories=max_stories,
        source_share=source_share,
    )
    return {
        'id': 'live-preview',
        'kind': 'preview',
        'date': now.date().isoformat(),
        'published_at': now.isoformat(),
        'article_count': len(selected),
        'articles': selected,
        'selection_report': selection_report,
        'preview': True,
        'preview_message': 'Built live from the current digest; the immutable archive is unchanged.',
    }


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
