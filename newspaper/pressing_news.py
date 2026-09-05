"""Strict selector for consequential, fast-moving breaking news."""
import re
from datetime import datetime, timedelta, timezone

MAX_ITEMS = 10
MAX_AGE_HOURS = 18
NEWS_CATEGORIES = {'worldnews', 'brazilnews', 'world'}
MAJOR_SOURCES = {
    'reuters', 'bbc', 'bbc news', 'bbc world', 'bbc us & canada', 'financial times',
    'financial times world', 'financial times us', 'the guardian', 'guardian',
    'associated press', 'ap news', 'agência brasil', 'agencia brasil',
    'g1 brasil', 'globo', 'folha de s.paulo', 'o globo',
    'new york times', 'new york times world', 'new york times us',
    'washington post',
}
EXCLUDE = re.compile(r'\b(opinion|commentary|podcast|quiz|review|explainer|week in pictures)\b', re.I)
SIGNALS = (
    ('Catastrophe or public emergency', re.compile(
        r'\b(earthquake|tsunami|hurricane|typhoon|tornado|wildfire|flash flood|'
        r'volcanic eruption|major explosion|mass shooting|state of emergency|'
        r'evacuation(?:s)? ordered|disaster declaration)\b', re.I)),
    ('Major conflict or security development', re.compile(
        r'\b(invasion|ceasefire|declares war|airstrike|missile attack|military coup|'
        r'assassinat(?:ed|ion)|hostage release|nuclear alert|terror attack)\b', re.I)),
    ('Major political or diplomatic development', re.compile(
        r'\b(resigns?|steps down|impeach(?:ed|ment)|election results?|wins? election|'
        r'emergency summit|peace agreement|peace deal|major sanctions|'
        r'(?:u[.]?s[.]?|american|trump) envoys?.{0,80}(?:meet\w*|talks?).{0,40}putin|'
        r'putin.{0,80}(?:meets?|talks? with).{0,40}(?:u[.]?s[.]?|american|trump) envoys?)\b', re.I)),
    ('Major public address or announcement', re.compile(
        r'\b(address(?:es|ed)? (?:the )?nation|national address|major speech|'
        r'emergency address|announces? (?:a )?(?:ceasefire|state of emergency|'
        r'national emergency|major agreement))\b', re.I)),
    ('Exceptional economic or institutional event', re.compile(
        r'\b(market crash|bank collapse|sovereign default|emergency rate cut|'
        r'emergency rate hike|government shutdown|constitutional crisis)\b', re.I)),
)


def _parse_time(value):
    try:
        return datetime.fromisoformat(str(value or '').replace('Z', '+00:00')).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _signal(article):
    # The headline carries admission. A generic headline must not enter merely
    # because its body happens to mention a war or storm.
    title = str(article.get('title') or '')
    for reason, pattern in SIGNALS:
        if pattern.search(title):
            if reason == 'Catastrophe or public emergency' and re.search(
                    r'\b(earthquake|wildfire|flash flood|major explosion)\b', title, re.I):
                if not re.search(r'\b(major|powerful|deadly|kills?|deaths?|evacuat\w*|'
                                 r'emergency|magnitude|hundreds?|thousands?|devastat\w*|'
                                 r'record|catastroph\w*)\b', title, re.I):
                    return None
            return reason
    return None


def select(digest, now=None):
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cutoff = now - timedelta(hours=MAX_AGE_HOURS)
    candidates, seen = [], set()
    rejected = {'old': 0, 'outside_scope': 0, 'insufficient_significance': 0,
                'weak_confirmation': 0}
    for article in digest.get('articles') or []:
        if article.get('cluster_rep') is False:
            continue
        identity = article.get('cluster_id') or article.get('story_fingerprint') or article.get('id')
        if not identity or identity in seen:
            continue
        seen.add(identity)
        if str(article.get('category') or '').casefold() not in NEWS_CATEGORIES:
            rejected['outside_scope'] += 1
            continue
        published = _parse_time(article.get('published_at'))
        if not published or published < cutoff or published > now + timedelta(minutes=10):
            rejected['old'] += 1
            continue
        text = f"{article.get('title') or ''} {article.get('summary') or ''}"
        evidence_sources = {
            str(article.get('editorial_source') or article.get('source') or '').strip().casefold()
        }
        for evidence in article.get('corroborating_sources') or []:
            if isinstance(evidence, dict):
                value = evidence.get('editorial_source') or evidence.get('source')
            else:
                value = evidence
            if str(value or '').strip():
                evidence_sources.add(str(value).strip().casefold())
        evidence_sources.discard('')
        corroboration = len(evidence_sources)
        reason = _signal(article)
        if not reason and corroboration >= 3 and float(article.get('score') or 0) >= 8:
            reason = 'Major developing story confirmed by multiple outlets'
        if not reason or EXCLUDE.search(text):
            rejected['insufficient_significance'] += 1
            continue
        source = str(article.get('editorial_source') or article.get('source') or '').casefold()
        if source not in MAJOR_SOURCES and corroboration < 2:
            rejected['weak_confirmation'] += 1
            continue
        item = dict(article)
        item['hot_metal_reason'] = reason
        item['hot_metal_corroboration'] = corroboration
        candidates.append(item)
    candidates.sort(key=lambda item: (
        -int(item.get('hot_metal_corroboration') or 1),
        -float(item.get('score') or 0),
        -(_parse_time(item.get('published_at')) or datetime.min.replace(tzinfo=timezone.utc)).timestamp(),
    ))
    selected = candidates[:MAX_ITEMS]
    return {
        'id': 'hot-metal', 'kind': 'hot_metal',
        'generated_at': digest.get('generated_at'),
        'article_count': len(selected), 'articles': selected,
        'criteria': {'max_age_hours': MAX_AGE_HOURS, 'max_items': MAX_ITEMS,
                     'scope': 'Consequential breaking world and Brazil headlines only'},
        'selection_report': {'admitted': len(selected), 'rejected': rejected},
    }
