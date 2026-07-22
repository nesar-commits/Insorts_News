import logging
import re
from datetime import datetime, timedelta, timezone
from time import mktime
from urllib.parse import urlparse

import feedparser
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.article import Article
from app.models.category import Category
from app.models.source import Source
from app.services.rss_sources import CATEGORIES, FEEDS

logger = logging.getLogger("rss_ingest")

IMG_TAG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

META_TAG_RE = re.compile(r"<meta\s+[^>]*>", re.IGNORECASE)
META_PROPERTY_RE = re.compile(r'(?:property|name)=["\'](og:image|twitter:image)["\']', re.IGNORECASE)
META_CONTENT_RE = re.compile(r'content=["\']([^"\']+)["\']', re.IGNORECASE)

_HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; InsortsNewsBot/1.0; +https://insortsnews.example)"}

# Some sources occasionally republish the identical story under a second URL
# within minutes (seen from Al Jazeera). Only collapse same-source articles
# that share an exact title AND were published within this window — genuinely
# distinct content that happens to share a generic title (e.g. a recurring
# BBC podcast episode) is always published far apart in time, so it's safe.
DUPLICATE_TITLE_WINDOW = timedelta(hours=6)


def _fetch_og_image(article_url: str, timeout: float = 5.0) -> str | None:
    """Best-effort fallback: some RSS feeds embed no image at all, but the
    article's own page almost always has an og:image/twitter:image meta tag
    for social-link previews. Never raises — a miss here just means we keep
    the gradient placeholder, which is an acceptable outcome, not an error.
    """
    try:
        response = httpx.get(
            article_url, timeout=timeout, follow_redirects=True, headers=_HTTP_HEADERS
        )
        if response.status_code != 200:
            return None
        html = response.text[:200_000]  # meta tags always live in <head>, no need to scan further
    except Exception:
        return None

    found = {}
    for tag in META_TAG_RE.findall(html):
        prop_match = META_PROPERTY_RE.search(tag)
        content_match = META_CONTENT_RE.search(tag)
        if prop_match and content_match:
            found[prop_match.group(1).lower()] = content_match.group(1)

    return found.get("og:image") or found.get("twitter:image")


def ensure_categories_and_sources(db: Session) -> None:
    slug_to_category = {}
    for cat in CATEGORIES:
        existing = db.query(Category).filter(Category.slug == cat["slug"]).first()
        if not existing:
            existing = Category(name=cat["name"], slug=cat["slug"], icon=cat["icon"])
            db.add(existing)
            db.flush()
        slug_to_category[cat["slug"]] = existing
    db.commit()

    for name, feed_url, site_url, category_slug in FEEDS:
        existing = db.query(Source).filter(Source.feed_url == feed_url).first()
        if not existing:
            category = slug_to_category[category_slug]
            db.add(Source(name=name, feed_url=feed_url, site_url=site_url, category_id=category.id))
    db.commit()


_BOGUS_SEGMENTS = ("undefined", "null", "none")


def _is_valid_image_url(url: str | None) -> bool:
    """Guards against garbage some feeds occasionally emit — e.g. NPR's feed
    has been observed to include a <link type="image/..."> whose href is the
    literal string "undefined". feedparser resolves that relative href into a
    full (but nonexistent) URL against the feed's own domain before we ever
    see it, so the check has to look at the resolved path's last segment too,
    not just reject the bare word.
    """
    if not url:
        return False
    stripped = url.strip()
    if stripped.lower() in _BOGUS_SEGMENTS:
        return False
    parsed = urlparse(stripped)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    last_segment = parsed.path.rstrip("/").rsplit("/", 1)[-1].lower()
    return last_segment not in _BOGUS_SEGMENTS


def _extract_image(entry) -> str | None:
    media_content = getattr(entry, "media_content", None)
    if media_content:
        url = media_content[0].get("url")
        if _is_valid_image_url(url):
            return url

    media_thumbnail = getattr(entry, "media_thumbnail", None)
    if media_thumbnail:
        url = media_thumbnail[0].get("url")
        if _is_valid_image_url(url):
            return url

    for link in getattr(entry, "links", []):
        if link.get("type", "").startswith("image/") and _is_valid_image_url(link.get("href")):
            return link.get("href")

    summary = getattr(entry, "summary", "") or ""
    match = IMG_TAG_RE.search(summary)
    if match and _is_valid_image_url(match.group(1)):
        return match.group(1)

    content_list = getattr(entry, "content", None) or []
    for block in content_list:
        match = IMG_TAG_RE.search(block.get("value", "") or "")
        if match and _is_valid_image_url(match.group(1)):
            return match.group(1)

    return None


def _parse_published(entry) -> datetime:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _clean_summary(entry) -> str | None:
    summary = getattr(entry, "summary", None)
    if not summary:
        return None
    text = re.sub(r"<[^>]+>", "", summary).strip()
    return text[:2000] if text else None


def _is_recent_duplicate(db: Session, source: Source, title: str, published_at: datetime) -> bool:
    return (
        db.query(Article.id)
        .filter(
            Article.source_id == source.id,
            Article.title == title,
            Article.published_at >= published_at - DUPLICATE_TITLE_WINDOW,
            Article.published_at <= published_at + DUPLICATE_TITLE_WINDOW,
        )
        .first()
        is not None
    )


def fetch_and_store_source(db: Session, source: Source) -> int:
    parsed = feedparser.parse(source.feed_url)
    new_count = 0
    seen_urls: set[str] = set()
    seen_titles_this_batch: set[str] = set()

    for entry in parsed.entries[:50]:
        url = getattr(entry, "link", None)
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        exists = db.query(Article.id).filter(Article.url == url).first()
        if exists:
            continue

        title = (getattr(entry, "title", None) or "Untitled")[:500]
        published_at = _parse_published(entry)

        if title in seen_titles_this_batch:
            continue
        if _is_recent_duplicate(db, source, title, published_at):
            continue
        seen_titles_this_batch.add(title)

        image_url = _extract_image(entry) or _fetch_og_image(url)
        if not _is_valid_image_url(image_url):
            image_url = None

        article = Article(
            title=title,
            summary=_clean_summary(entry),
            url=url,
            image_url=image_url,
            author=getattr(entry, "author", None),
            source_id=source.id,
            category_id=source.category_id,
            published_at=published_at,
        )
        db.add(article)
        new_count += 1

    if new_count:
        db.commit()
    return new_count


def delete_stale_articles(db: Session, retention_days: int) -> int:
    """Purges articles older than the retention window — but never one a user
    has bookmarked, since the whole point of saving an article is to keep it
    around longer than the feed's normal lifespan.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = (
        db.query(Article)
        .filter(Article.published_at < cutoff)
        .filter(~Article.bookmarked_by.any())
        .delete(synchronize_session=False)
    )
    if deleted:
        db.commit()
    return deleted


def fetch_and_store_all(db: Session) -> int:
    ensure_categories_and_sources(db)

    total_new = 0
    for source in db.query(Source).all():
        try:
            total_new += fetch_and_store_source(db, source)
        except Exception:
            logger.exception("Failed to fetch feed %s (%s)", source.name, source.feed_url)
            db.rollback()

    deleted = delete_stale_articles(db, settings.ARTICLE_RETENTION_DAYS)
    if deleted:
        logger.info("Deleted %d articles older than %d days", deleted, settings.ARTICLE_RETENTION_DAYS)

    logger.info("RSS ingest complete: %d new articles", total_new)
    return total_new
