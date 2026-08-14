from pydantic import BaseModel


class MutedPreferences(BaseModel):
    muted_source_ids: list[int]
    muted_category_ids: list[int]
