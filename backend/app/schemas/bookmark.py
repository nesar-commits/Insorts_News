from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    article_id: int
