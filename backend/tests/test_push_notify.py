from unittest.mock import MagicMock

import pytest
import requests
from pywebpush import WebPushException

from app.services import push_notify


class FakeSubscription:
    def __init__(self, id, endpoint=None):
        self.id = id
        self.endpoint = endpoint or f"https://example.com/{id}"
        self.p256dh = "p"
        self.auth = "a"


@pytest.fixture(autouse=True)
def vapid_keys(monkeypatch):
    monkeypatch.setattr(push_notify.settings, "VAPID_PRIVATE_KEY", "priv")
    monkeypatch.setattr(push_notify.settings, "VAPID_PUBLIC_KEY", "pub")


def test_returns_zero_and_skips_when_vapid_not_configured(monkeypatch):
    monkeypatch.setattr(push_notify.settings, "VAPID_PRIVATE_KEY", "")
    monkeypatch.setattr(push_notify, "get_all_subscriptions", lambda db: [FakeSubscription(1)])

    sent = push_notify.send_push_to_all(MagicMock(), "title", "body")

    assert sent == 0


def test_a_transport_error_does_not_abort_the_rest_of_the_batch(monkeypatch):
    subs = [FakeSubscription(1), FakeSubscription(2), FakeSubscription(3)]
    monkeypatch.setattr(push_notify, "get_all_subscriptions", lambda db: subs)

    calls = []

    def fake_webpush(**kwargs):
        endpoint = kwargs["subscription_info"]["endpoint"]
        calls.append(endpoint)
        if endpoint == subs[1].endpoint:
            raise requests.exceptions.ConnectionError("dead endpoint")

    monkeypatch.setattr(push_notify, "webpush", fake_webpush)

    sent = push_notify.send_push_to_all(MagicMock(), "title", "body")

    # subscriber #2's dead endpoint must not stop #3 from being reached
    assert [s.endpoint for s in subs] == calls
    assert sent == 2


def test_a_404_response_prunes_the_subscription(monkeypatch):
    sub = FakeSubscription(1)
    monkeypatch.setattr(push_notify, "get_all_subscriptions", lambda db: [sub])
    pruned = []
    monkeypatch.setattr(push_notify, "delete_subscription_by_id", lambda db, sub_id: pruned.append(sub_id))

    response = MagicMock(status_code=404)

    def fake_webpush(**kwargs):
        raise WebPushException("gone", response=response)

    monkeypatch.setattr(push_notify, "webpush", fake_webpush)

    sent = push_notify.send_push_to_all(MagicMock(), "title", "body")

    assert sent == 0
    assert pruned == [1]


def test_all_subscribers_reached_when_none_fail(monkeypatch):
    subs = [FakeSubscription(1), FakeSubscription(2)]
    monkeypatch.setattr(push_notify, "get_all_subscriptions", lambda db: subs)
    monkeypatch.setattr(push_notify, "webpush", lambda **kwargs: None)

    sent = push_notify.send_push_to_all(MagicMock(), "title", "body")

    assert sent == 2
