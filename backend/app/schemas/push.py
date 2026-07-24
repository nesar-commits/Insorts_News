import ipaddress
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(max_length=1000)
    keys: PushKeys

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        # The backend later makes an outbound POST to this exact URL (see
        # push_notify.py) — without this check, anyone could point it at an
        # internal service or cloud metadata endpoint (SSRF) via a fake but
        # schema-valid subscription. Real push services are always a real
        # https hostname, never a raw IP or localhost.
        parsed = urlparse(value)
        if parsed.scheme != "https":
            raise ValueError("endpoint must be an https:// URL")
        hostname = parsed.hostname or ""
        if not hostname or hostname == "localhost":
            raise ValueError("invalid endpoint host")
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            raise ValueError("endpoint host must not be a raw IP address")
        return value


class VapidPublicKey(BaseModel):
    key: str
