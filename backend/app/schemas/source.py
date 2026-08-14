from pydantic import BaseModel, ConfigDict


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category_id: int
    site_url: str | None = None
    logo_url: str | None = None
