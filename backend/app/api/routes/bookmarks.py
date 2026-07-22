import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.article import get_article
from app.crud.bookmark import (
    create_bookmark,
    delete_bookmark,
    get_bookmark,
    get_user_bookmarked_articles,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.article import ArticleRead, PaginatedArticles
from app.schemas.bookmark import BookmarkCreate

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("", response_model=PaginatedArticles)
def list_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = get_user_bookmarked_articles(db, current_user.id, page=page, page_size=page_size)
    articles = []
    for article in items:
        data = ArticleRead.model_validate(article)
        data.is_bookmarked = True
        articles.append(data)

    return PaginatedArticles(
        items=articles,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.post("", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
def add_bookmark(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = get_article(db, bookmark_in.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not get_bookmark(db, current_user.id, article.id):
        create_bookmark(db, current_user.id, article.id)

    data = ArticleRead.model_validate(article)
    data.is_bookmarked = True
    return data


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = get_bookmark(db, current_user.id, article_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    delete_bookmark(db, bookmark)
