from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.bookmark import Bookmark


def get_bookmark(db: Session, user_id: int, article_id: int) -> Bookmark | None:
    return (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.article_id == article_id)
        .first()
    )


def create_bookmark(db: Session, user_id: int, article_id: int) -> Bookmark:
    bookmark = Bookmark(user_id=user_id, article_id=article_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def delete_bookmark(db: Session, bookmark: Bookmark) -> None:
    db.delete(bookmark)
    db.commit()


def get_user_bookmarked_articles(
    db: Session, user_id: int, page: int = 1, page_size: int = 20
) -> tuple[list[Article], int]:
    query = (
        db.query(Article)
        .join(Bookmark, Bookmark.article_id == Article.id)
        .options(joinedload(Article.source), joinedload(Article.category))
        .filter(Bookmark.user_id == user_id)
    )

    total = query.with_entities(func.count(Article.id)).scalar() or 0

    items = (
        query.order_by(Bookmark.created_at.desc(), Bookmark.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
