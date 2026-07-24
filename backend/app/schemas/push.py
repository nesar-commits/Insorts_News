from pydantic import BaseModel, Field


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(max_length=1000)
    keys: PushKeys


class VapidPublicKey(BaseModel):
    key: str
