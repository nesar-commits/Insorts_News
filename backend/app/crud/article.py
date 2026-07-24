from datetime import datetime

from sqlalchemy import func, or_, tuple_
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.source import Source


def get_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.query(Category).filter(Category.slug == slug).first()


def get_articles(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_slug: str | None = None,
    search: str | None = None,
    cursor: tuple[datetime, int] | None = None,
    region: str | None = None,
) -> tuple[list[Article], int]:
    query = db.query(Article).options(joinedload(Article.source), joinedload(Article.category))

    if category_slug and category_slug != "all":
        query = query.join(Category).filter(Category.slug == category_slug)

    if region:
        query = query.join(Source, Article.source_id == Source.id).filter(Source.region == region)

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


def get_article(db: Session, article_id: int) -> Article | None:
    return (
        db.query(Article)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )


def get_bookmarked_article_ids(db: Session, user_id: int, article_ids: list[int]) -> set[int]:
    if not article_ids:
        return set()
    rows = (
        db.query(Bookmark.article_id)
        .filter(Bookmark.user_id == user_id, Bookmark.article_id.in_(article_ids))
        .all()
    )
    return {row[0] for row in rows}
