from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.category import Category


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
) -> tuple[list[Article], int]:
    query = db.query(Article).options(joinedload(Article.source), joinedload(Article.category))

    if category_slug and category_slug != "all":
        query = query.join(Category).filter(Category.slug == category_slug)

    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{escaped}%"
        query = query.filter(
            or_(Article.title.ilike(like, escape="\\"), Article.summary.ilike(like, escape="\\"))
        )

    total = query.with_entities(func.count(Article.id)).scalar() or 0

    items = (
        query.order_by(Article.published_at.desc(), Article.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


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
