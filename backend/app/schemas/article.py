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
    page: int
    page_size: int
    total: int
    total_pages: int
