import logging
from urllib.parse import quote

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.source import Source
from app.services.rss_ingest import fetch_and_store_source

logger = logging.getLogger("dynamic_city")


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
        name=f"Local news: {city}",
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
