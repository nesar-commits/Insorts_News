from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryRead


class SourceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    logo_url: str | None = None
    site_url: str | None = None


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None = None
    url: str
    image_url: str | None = None
    author: str | None = None
    published_at: datetime
    source: SourceBrief
    category: CategoryRead
    is_bookmarked: bool = False


class PaginatedArticles(BaseModel):
    items: list[ArticleRead]
    total: int
    # Offset-pagination fields — still used by /bookmarks, which isn't
    # subject to the concurrent insert/delete churn the RSS job causes.
    page: int | None = None
    page_size: int | None = None
    total_pages: int | None = None
    # Keyset-pagination field — used by /articles' infinite scroll instead,
    # since that list actually changes under the reader while they scroll.
    next_cursor: str | None = None
