import ipaddress
import socket
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(max_length=1000)
    keys: PushKeys
    # None (the default, if the client never sends this field) means "every
    # category" — an empty list would instead mean "opted out of all
    # breaking-news categories", which is a real but different preference.
    category_ids: list[int] | None = None

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        # The backend later makes an outbound POST to this exact URL (see
        # push_notify.py) — without this check, anyone could point it at an
        # internal service or cloud metadata endpoint (SSRF) via a fake but
        # schema-valid subscription. Real push services are always a real
        # https hostname, never a raw IP or localhost.
        #
        # Checking the hostname string itself (e.g. rejecting anything
        # ipaddress.ip_address() parses) isn't enough: that function only
        # recognizes canonical dotted-decimal/hex-IPv6 notation, while the
        # resolver actually used to make the outbound request also accepts
        # decimal/octal/hex-encoded IPv4 forms (e.g. "2852039166" resolves
        # to 169.254.169.254, the cloud metadata address) that sail right
        # past a string check. Resolving the hostname and checking the real
        # IP(s) it points to is the only check that can't be bypassed by
        # re-encoding the same address differently.
        parsed = urlparse(value)
        if parsed.scheme != "https":
            raise ValueError("endpoint must be an https:// URL")
        hostname = parsed.hostname or ""
        if not hostname:
            raise ValueError("invalid endpoint host")
        try:
            resolved_ips = {info[4][0] for info in socket.getaddrinfo(hostname, 443)}
        except OSError:
            raise ValueError("endpoint host does not resolve")
        for ip_str in resolved_ips:
            addr = ipaddress.ip_address(ip_str)
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved or addr.is_multicast:
                raise ValueError("endpoint host must not resolve to a private/internal address")
        return value


class VapidPublicKey(BaseModel):
    key: str


class PushCategoryUpdate(BaseModel):
    # No SSRF-style validation here (unlike PushSubscriptionCreate) — this
    # never makes an outbound request itself, it only looks up an existing
    # row by (endpoint, keys) as proof of ownership, same as unsubscribe.
    endpoint: str = Field(max_length=1000)
    keys: PushKeys
    category_ids: list[int]
