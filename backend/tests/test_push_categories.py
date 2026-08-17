import pytest

from app.crud.push_subscription import (
    get_subscription_category_ids,
    set_subscription_categories,
    upsert_subscription,
)
from app.models.category import Category
from app.services import push_notify

VALID_KEYS = {"p256dh": "p", "auth": "a"}


def _subscribe(client, endpoint, category_ids=None):
    payload = {"endpoint": endpoint, "keys": VALID_KEYS}
    if category_ids is not None:
        payload["category_ids"] = category_ids
    return client.post("/api/push/subscribe", json=payload)


@pytest.fixture(autouse=True)
def resolve_locally(monkeypatch):
    # Push endpoints go through the SSRF-safety hostname resolution — use a
    # fake https URL whose host resolves locally so these tests don't hit
    # real network/DNS.
    import socket

    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *a, **k: [(None, None, None, None, ("93.184.216.34", 443))]
    )


def test_subscribe_with_no_category_ids_means_all_categories(client, db_session):
    response = _subscribe(client, "https://push.example.com/a")
    assert response.status_code == 204

    sub = upsert_subscription(db_session, "https://push.example.com/a", "p", "a")
    assert get_subscription_category_ids(db_session, sub.id) == set()


def test_subscribe_with_category_ids_persists_them(client, db_session):
    response = _subscribe(client, "https://push.example.com/a2", category_ids=[1, 2])
    assert response.status_code == 204

    sub = upsert_subscription(db_session, "https://push.example.com/a2", "p", "a")
    assert get_subscription_category_ids(db_session, sub.id) == {1, 2}


def test_update_categories_requires_matching_ownership_keys(client):
    _subscribe(client, "https://push.example.com/b", category_ids=[1])

    response = client.put(
        "/api/push/categories",
        json={"endpoint": "https://push.example.com/b", "keys": {"p256dh": "wrong", "auth": "wrong"}, "category_ids": [2]},
    )
    assert response.status_code == 404


def test_update_categories_succeeds_with_correct_keys(client):
    _subscribe(client, "https://push.example.com/c", category_ids=[1])

    response = client.put(
        "/api/push/categories",
        json={"endpoint": "https://push.example.com/c", "keys": VALID_KEYS, "category_ids": [2, 3]},
    )
    assert response.status_code == 204


def test_send_push_to_all_only_reaches_subscribers_opted_into_that_category(monkeypatch, db_session, category):
    monkeypatch.setattr(push_notify.settings, "VAPID_PRIVATE_KEY", "priv")
    monkeypatch.setattr(push_notify.settings, "VAPID_PUBLIC_KEY", "pub")

    other_category = Category(name="Other", slug="other")
    db_session.add(other_category)
    db_session.commit()

    all_categories_sub = upsert_subscription(db_session, "https://push.example.com/all", "p", "a")
    other_only_sub = upsert_subscription(db_session, "https://push.example.com/other", "p", "a")
    set_subscription_categories(db_session, other_only_sub.id, [other_category.id])

    sent_endpoints = []
    monkeypatch.setattr(
        push_notify,
        "webpush",
        lambda **kwargs: sent_endpoints.append(kwargs["subscription_info"]["endpoint"]),
    )

    push_notify.send_push_to_all(db_session, "t", "b", category_id=category.id)

    assert all_categories_sub.endpoint in sent_endpoints
    assert other_only_sub.endpoint not in sent_endpoints


def test_send_push_to_all_reaches_a_subscriber_specifically_opted_into_that_category(monkeypatch, db_session, category):
    monkeypatch.setattr(push_notify.settings, "VAPID_PRIVATE_KEY", "priv")
    monkeypatch.setattr(push_notify.settings, "VAPID_PUBLIC_KEY", "pub")

    sub = upsert_subscription(db_session, "https://push.example.com/opted-in", "p", "a")
    set_subscription_categories(db_session, sub.id, [category.id])

    sent_endpoints = []
    monkeypatch.setattr(
        push_notify,
        "webpush",
        lambda **kwargs: sent_endpoints.append(kwargs["subscription_info"]["endpoint"]),
    )

    push_notify.send_push_to_all(db_session, "t", "b", category_id=category.id)

    assert sub.endpoint in sent_endpoints


def test_empty_category_ids_means_opted_out_of_every_category_not_all(client, db_session, category):
    # Regression test: category_ids=[] must NOT be indistinguishable from
    # "no preference set" (which means every category) — previously both
    # states stored zero PushSubscriptionCategory rows, so opting out of
    # everything silently turned into opting into everything.
    _subscribe(client, "https://push.example.com/opt-out", category_ids=[1])

    response = client.put(
        "/api/push/categories",
        json={"endpoint": "https://push.example.com/opt-out", "keys": VALID_KEYS, "category_ids": []},
    )
    assert response.status_code == 204

    sub = upsert_subscription(db_session, "https://push.example.com/opt-out", "p", "a")
    assert get_subscription_category_ids(db_session, sub.id) == set()
    assert sub.receives_all_categories is False


def test_send_push_to_all_does_not_reach_a_subscriber_opted_out_of_every_category(monkeypatch, db_session, category):
    monkeypatch.setattr(push_notify.settings, "VAPID_PRIVATE_KEY", "priv")
    monkeypatch.setattr(push_notify.settings, "VAPID_PUBLIC_KEY", "pub")

    opted_out_sub = upsert_subscription(db_session, "https://push.example.com/opted-out", "p", "a")
    set_subscription_categories(db_session, opted_out_sub.id, [])

    all_categories_sub = upsert_subscription(db_session, "https://push.example.com/still-all", "p", "a")

    sent_endpoints = []
    monkeypatch.setattr(
        push_notify,
        "webpush",
        lambda **kwargs: sent_endpoints.append(kwargs["subscription_info"]["endpoint"]),
    )

    push_notify.send_push_to_all(db_session, "t", "b", category_id=category.id)

    assert opted_out_sub.endpoint not in sent_endpoints
    assert all_categories_sub.endpoint in sent_endpoints


def test_setting_category_ids_to_none_resets_to_all_categories(db_session, category):
    sub = upsert_subscription(db_session, "https://push.example.com/reset", "p", "a")
    set_subscription_categories(db_session, sub.id, [category.id])
    assert sub.receives_all_categories is False

    set_subscription_categories(db_session, sub.id, None)
    db_session.refresh(sub)
    assert sub.receives_all_categories is True
    assert get_subscription_category_ids(db_session, sub.id) == set()


def test_delete_subscription_with_category_filters_succeeds(client, db_session, category):
    from app.crud.push_subscription import delete_subscription, get_all_subscriptions

    sub = upsert_subscription(db_session, "https://push.example.com/del-filter", "p", "a")
    set_subscription_categories(db_session, sub.id, [category.id])

    delete_subscription(db_session, "https://push.example.com/del-filter", "p", "a")
    assert sub not in get_all_subscriptions(db_session)


def test_delete_subscription_by_id_with_category_filters_succeeds(db_session, category):
    from app.crud.push_subscription import delete_subscription_by_id, get_all_subscriptions

    sub = upsert_subscription(db_session, "https://push.example.com/del-filter-id", "p", "a")
    set_subscription_categories(db_session, sub.id, [category.id])

    delete_subscription_by_id(db_session, sub.id)
    assert sub not in get_all_subscriptions(db_session)

