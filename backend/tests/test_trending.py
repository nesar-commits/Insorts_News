from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import make_article, make_source


def test_view_endpoint_increments_count_and_404s_for_missing_article(client, db_session, category):
    source = make_source(db_session, category)
    article = make_article(db_session, source, category)

    response = client.post(f"/api/articles/{article.id}/view")
    assert response.status_code == 204

    db_session.refresh(article)
    assert article.view_count == 1

    missing = client.post("/api/articles/999999/view")
    assert missing.status_code == 404


def test_trending_ranks_by_view_count_within_window(client, db_session, category):
    source = make_source(db_session, category)
    now = datetime.now(timezone.utc)
    low = make_article(db_session, source, category, title="Low views", published_at=now - timedelta(hours=1))
    high = make_article(db_session, source, category, title="High views", published_at=now - timedelta(hours=2))

    for _ in range(5):
        client.post(f"/api/articles/{high.id}/view")
    client.post(f"/api/articles/{low.id}/view")

    response = client.get("/api/articles/trending")
    titles = [a["title"] for a in response.json()]
    assert titles.index("High views") < titles.index("Low views")


def test_trending_excludes_articles_outside_the_window(client, db_session, category):
    # With a limit of 1 and two candidates, the ranked (viewed, in-window)
    # article must win over the filler picking the old one just because
    # it's the only thing left — proving the window filter, not just the
    # "never show fewer than limit" fallback, is what's doing the exclusion.
    source = make_source(db_session, category)
    old = make_article(
        db_session,
        source,
        category,
        title="Old but viewed",
        published_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    client.post(f"/api/articles/{old.id}/view")
    make_article(db_session, source, category, title="New and unviewed")

    response = client.get("/api/articles/trending", params={"limit": 1})
    titles = [a["title"] for a in response.json()]
    assert titles == ["New and unviewed"]


def test_trending_fills_remaining_slots_with_recent_articles_when_no_views(client, db_session, category):
    source = make_source(db_session, category)
    make_article(db_session, source, category, title="Unviewed recent")

    response = client.get("/api/articles/trending", params={"limit": 5})
    titles = [a["title"] for a in response.json()]
    assert "Unviewed recent" in titles


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "trend@example.com", "username": "trendfan", "password": "hunter22-battery"},
    )
    login = client.post("/api/auth/login", json={"email": "trend@example.com", "password": "hunter22-battery"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_trending_excludes_muted_source_for_that_user(client, db_session, category, auth_headers):
    muted_source = make_source(db_session, category)
    other_source = make_source(db_session, category)
    muted_article = make_article(db_session, muted_source, category, title="From muted source")
    other_article = make_article(db_session, other_source, category, title="From other source")
    client.post(f"/api/articles/{muted_article.id}/view")
    client.post(f"/api/articles/{other_article.id}/view")

    client.post(f"/api/users/me/muted-sources/{muted_source.id}", headers=auth_headers)

    response = client.get("/api/articles/trending", headers=auth_headers)
    titles = [a["title"] for a in response.json()]
    assert "From muted source" not in titles
    assert "From other source" in titles
