import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.source import Source
from app.services.rss_ingest import fetch_and_store_source

logger = logging.getLogger("dynamic_city")

# Matches Source.city's column width — truncate here (once, at detection
# time in the caller) rather than at creation time, so the exact same
# string is used consistently for cooldown-keying, existence lookups, and
# the stored row; truncating only on insert would make future lookups with
# the untruncated name never match, defeating the cooldown below entirely.
CITY_NAME_MAX_LENGTH = 50

CITY_ATTEMPT_COOLDOWN = timedelta(hours=1)
MAX_NEW_CITIES_PER_HOUR = 20

_last_attempt_at: dict[str, datetime] = {}
_creation_times: list[datetime] = []


def should_attempt_city_creation(city: str) -> bool:
    """Gatekeeper the route calls before queuing a background task.

    Without this, two real problems show up: (1) a city whose feed nets
    zero usable articles gets re-fetched from Google News on every single
    subsequent request from that city, forever — there's otherwise no
    signal that an attempt already happened; (2) since this whole path is
    unauthenticated and lat/lon are just range-validated query params, a
    client could script requests across many coordinates to cheaply force
    unbounded outbound requests / Source rows.
    """
    now = datetime.now(timezone.utc)
    key = city.lower()

    last_attempt = _last_attempt_at.get(key)
    if last_attempt and now - last_attempt < CITY_ATTEMPT_COOLDOWN:
        return False

    global _creation_times
    _creation_times = [t for t in _creation_times if now - t < timedelta(hours=1)]
    if len(_creation_times) >= MAX_NEW_CITIES_PER_HOUR:
        logger.warning("Dynamic city creation rate cap hit — skipping %s this cycle", city)
        return False

    _last_attempt_at[key] = now
    _creation_times.append(now)
    return True


def google_news_city_feed_url(city: str) -> str:
    # The /search endpoint works reliably for literally any place name
    # worldwide (verified against e.g. Ulaanbaatar, Tokyo, Buenos Aires) —
    # unlike the /headlines/section/geo/ endpoint, which silently returns
    # nothing for many real cities.
    return f"https://news.google.com/rss/search?q={quote(city)}&hl=en-US&gl=US&ceid=US:en"


def _get_or_create_city_source(db: Session, city: str, region: str | None) -> Source:
    existing = db.query(Source).filter(func.lower(Source.city) == city.lower()).first()
    if existing:
        return existing

    category = db.query(Category).filter(Category.slug == "general").first()
    feed_url = google_news_city_feed_url(city)
    source = Source(
        name=f"Local news: {city}"[:100],
        feed_url=feed_url,
        site_url="https://news.google.com",
        category_id=category.id,
        region=region,
        language="en",
        city=city,
    )
    try:
        db.add(source)
        db.commit()
        return source
    except IntegrityError:
        # Another request for the same city raced us and won.
        db.rollback()
        return db.query(Source).filter(Source.feed_url == feed_url).first()


def ensure_dynamic_city_source(city: str, region: str | None) -> None:
    """Runs as a FastAPI BackgroundTask, after the triggering request has
    already been sent its (fallback) response — this is what makes a brand
    new city "just work" on the *next* visit instead of failing the first
    one, without making anyone wait on a live fetch.
    """
    db = SessionLocal()
    try:
        source = _get_or_create_city_source(db, city, region)
        if source:
            new_articles = fetch_and_store_source(db, source, fetch_missing_images=False)
            logger.info("Dynamic city source ready for %s: %d new articles", city, len(new_articles))
    except Exception:
        logger.exception("Failed to set up dynamic city source for %s", city)
        db.rollback()
    finally:
        db.close()
