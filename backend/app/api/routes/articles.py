import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.crud.article import get_article, get_articles, get_bookmarked_article_ids
from app.db.session import get_db
from app.models.user import User
from app.schemas.article import ArticleRead, PaginatedArticles

router = APIRouter(prefix="/articles", tags=["articles"])


def _to_article_read(article, bookmarked_ids: set[int]) -> ArticleRead:
    data = ArticleRead.model_validate(article)
    data.is_bookmarked = article.id in bookmarked_ids
    return data


@router.get("", response_model=PaginatedArticles)
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    category: str | None = Query(None, description="Category slug, or omit for all"),
    search: str | None = Query(None, min_length=1, max_length=200),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    items, total = get_articles(db, page=page, page_size=page_size, category_slug=category, search=search)

    bookmarked_ids = (
        get_bookmarked_article_ids(db, current_user.id, [a.id for a in items]) if current_user else set()
    )

    return PaginatedArticles(
        items=[_to_article_read(a, bookmarked_ids) for a in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/trending", response_model=list[ArticleRead])
def trending_articles(
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    items, _ = get_articles(db, page=1, page_size=limit)
    bookmarked_ids = (
        get_bookmarked_article_ids(db, current_user.id, [a.id for a in items]) if current_user else set()
    )
    return [_to_article_read(a, bookmarked_ids) for a in items]


@router.get("/{article_id}", response_model=ArticleRead)
def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    bookmarked_ids = get_bookmarked_article_ids(db, current_user.id, [article.id]) if current_user else set()
    return _to_article_read(article, bookmarked_ids)
