from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, tuple_
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.source import Source

# How far back /trending looks for its view-count signal — old enough that
# a single quiet hour doesn't starve it, recent enough that "trending" still
# means something distinct from "most-viewed ever".
TRENDING_WINDOW_HOURS = 48


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.query(Category).filter(Category.slug == slug).first()


def get_category(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_sources(db: Session) -> list[Source]:
    return db.query(Source).order_by(Source.name).all()


def get_source(db: Session, source_id: int) -> Source | None:
    return db.query(Source).filter(Source.id == source_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_slug: str | None = None,
    search: str | None = None,
    cursor: tuple[datetime, int] | None = None,
    region: str | None = None,
    language: str | None = None,
    city: str | None = None,
    excluded_source_ids: set[int] | None = None,
    excluded_category_ids: set[int] | None = None,
) -> tuple[list[Article], int]:
    query = db.query(Article).options(joinedload(Article.source), joinedload(Article.category))

    if category_slug and category_slug != "all":
        query = query.join(Category).filter(Category.slug == category_slug)

    if region or language or city:
        query = query.join(Source, Article.source_id == Source.id)
        if region:
            query = query.filter(Source.region == region)
        if language:
            query = query.filter(Source.language == language)
        if city:
            query = query.filter(func.lower(Source.city) == city.lower())

    if excluded_source_ids:
        query = query.filter(Article.source_id.notin_(excluded_source_ids))
    if excluded_category_ids:
        query = query.filter(Article.category_id.notin_(excluded_category_ids))

    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        query = query.filter(
            or_(Article.title.ilike(like, escape="\\"), Article.summary.ilike(like, escape="\\"))
        )

    total = query.with_entities(func.count(Article.id)).scalar() or 0

    query = query.order_by(Article.published_at.desc(), Article.id.desc())

    if cursor is not None:
        # Keyset pagination: anchor to the last-seen (published_at, id) rather
        # than a numeric offset, so articles inserted/deleted by the RSS job
        # between page fetches can't shift the window and duplicate or skip
        # a row — unlike OFFSET, this is stable under a concurrently-changing set.
        cursor_published_at, cursor_id = cursor
        items = (
            query.filter(tuple_(Article.published_at, Article.id) < (cursor_published_at, cursor_id))
            .limit(page_size)
            .all()
        )
    else:
        items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def region_has_articles(db: Session, region: str) -> bool:
    return (
        db.query(Article.id)
        .join(Source, Article.source_id == Source.id)
        .filter(Source.region == region)
        .first()
        is not None
    )


def region_and_language_has_articles(db: Session, region: str, language: str) -> bool:
    return (
        db.query(Article.id)
        .join(Source, Article.source_id == Source.id)
        .filter(Source.region == region, Source.language == language)
        .first()
        is not None
    )


def city_has_articles(db: Session, city: str) -> bool:
    return (
        db.query(Article.id)
        .join(Source, Article.source_id == Source.id)
        .filter(func.lower(Source.city) == city.lower())
        .first()
        is not None
    )


def city_and_language_has_articles(db: Session, city: str, language: str) -> bool:
    return (
        db.query(Article.id)
        .join(Source, Article.source_id == Source.id)
        .filter(func.lower(Source.city) == city.lower(), Source.language == language)
        .first()
        is not None
    )


def get_distinct_cities(db: Session) -> list[str]:
    rows = db.query(Source.city).filter(Source.city.isnot(None)).distinct().all()
    return [row[0] for row in rows]


def get_article(db: Session, article_id: int) -> Article | None:
    return (
        db.query(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )


def increment_view_count(db: Session, article_id: int) -> bool:
    """Returns False if the article doesn't exist, so the route can 404
    instead of silently no-opping. A bare UPDATE (not a fetch-then-save)
    avoids a race where two concurrent views on the same article both read
    the same starting count and one increment gets lost.
    """
    result = db.query(Article).filter(Article.id == article_id).update(
        {Article.view_count: Article.view_count + 1}, synchronize_session=False
    )
    db.commit()
    return result > 0


def get_trending_articles(
    db: Session,
    limit: int = 10,
    excluded_source_ids: set[int] | None = None,
    excluded_category_ids: set[int] | None = None,
) -> list[Article]:
    """Ranks by actual view_count within a recent window, not just publish
    recency — falls back to filling any remaining slots with the newest
    articles so a quiet window (e.g. right after deploy, before any views
    have landed) never shows fewer than `limit` items.
    """

    def _base_query():
        query = db.query(Article).options(joinedload(Article.source), joinedload(Article.category))
        if excluded_source_ids:
            query = query.filter(Article.source_id.notin_(excluded_source_ids))
        if excluded_category_ids:
            query = query.filter(Article.category_id.notin_(excluded_category_ids))
        return query

    cutoff = datetime.now(timezone.utc) - timedelta(hours=TRENDING_WINDOW_HOURS)
    trending = (
        _base_query()
        .filter(Article.published_at >= cutoff, Article.view_count > 0)
        .order_by(Article.view_count.desc(), Article.published_at.desc())
        .limit(limit)
        .all()
    )

    if len(trending) < limit:
        remaining = limit - len(trending)
        filler_query = _base_query().order_by(Article.published_at.desc(), Article.id.desc())
        existing_ids = {a.id for a in trending}
        if existing_ids:
            filler_query = filler_query.filter(Article.id.notin_(existing_ids))
        trending.extend(filler_query.limit(remaining).all())

    return trending


def get_bookmarked_article_ids(db: Session, user_id: int, article_ids: list[int]) -> set[int]:
    if not article_ids:
        return set()
    rows = (
        db.query(Bookmark.article_id)
        .filter(Bookmark.user_id == user_id, Bookmark.article_id.in_(article_ids))
        .all()
    )
    return {row[0] for row in rows}
