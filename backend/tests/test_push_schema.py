import socket

import pytest
from pydantic import ValidationError

from app.schemas.push import PushSubscriptionCreate

VALID_KEYS = {"p256dh": "a", "auth": "b"}


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://2852039166/x",  # decimal encoding of 169.254.169.254 (cloud metadata)
        "https://017700000001/x",  # octal encoding of 127.0.0.1
        "https://127.1/x",  # shorthand IPv4 form
        "https://127.0.0.1/x",
        "https://169.254.169.254/x",
        "https://localhost/x",
        "http://example.com/x",  # not https
    ],
)
def test_rejects_endpoints_resolving_to_private_or_non_https(endpoint):
    # These are all literal-address hostnames, so getaddrinfo resolves them
    # locally without a real DNS query — no network dependency here.
    with pytest.raises(ValidationError):
        PushSubscriptionCreate(endpoint=endpoint, keys=VALID_KEYS)


def test_rejects_endpoint_with_unresolvable_host(monkeypatch):
    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *a, **k: (_ for _ in ()).throw(socket.gaierror("no such host"))
    )
    with pytest.raises(ValidationError):
        PushSubscriptionCreate(endpoint="https://push.example.com/x", keys=VALID_KEYS)


def test_accepts_an_endpoint_that_resolves_to_a_public_address(monkeypatch):
    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *a, **k: [(None, None, None, None, ("142.250.0.1", 443))]
    )
    sub = PushSubscriptionCreate(endpoint="https://fcm.googleapis.com/fcm/send/abc123", keys=VALID_KEYS)
    assert sub.endpoint == "https://fcm.googleapis.com/fcm/send/abc123"
