import pytest

from tests.conftest import make_article, make_source


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "bookmarker@example.com", "username": "bookmarker", "password": "hunter22-battery"},
    )
    login = client.post(
        "/api/auth/login", json={"email": "bookmarker@example.com", "password": "hunter22-battery"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def article(db_session, category):
    source = make_source(db_session, category)
    return make_article(db_session, source, category)


def test_add_bookmark(client, auth_headers, article):
    response = client.post("/api/bookmarks", json={"article_id": article.id}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["is_bookmarked"] is True


def test_add_bookmark_requires_auth(client, article):
    response = client.post("/api/bookmarks", json={"article_id": article.id})

    assert response.status_code == 401


def test_add_bookmark_for_missing_article_404s(client, auth_headers):
    response = client.post("/api/bookmarks", json={"article_id": 999999}, headers=auth_headers)

    assert response.status_code == 404


def test_add_bookmark_is_idempotent(client, auth_headers, article):
    first = client.post("/api/bookmarks", json={"article_id": article.id}, headers=auth_headers)
    second = client.post("/api/bookmarks", json={"article_id": article.id}, headers=auth_headers)

    assert first.status_code == 201
    assert second.status_code == 201

    listing = client.get("/api/bookmarks", headers=auth_headers)
    assert listing.json()["total"] == 1


def test_list_bookmarks_only_returns_current_users(client, auth_headers, article, db_session, category):
    client.post("/api/bookmarks", json={"article_id": article.id}, headers=auth_headers)

    client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "username": "other", "password": "another-battery1"},
    )
    other_login = client.post(
        "/api/auth/login", json={"email": "other@example.com", "password": "another-battery1"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.get("/api/bookmarks", headers=other_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_remove_bookmark(client, auth_headers, article):
    client.post("/api/bookmarks", json={"article_id": article.id}, headers=auth_headers)

    response = client.delete(f"/api/bookmarks/{article.id}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get("/api/bookmarks", headers=auth_headers).json()["total"] == 0


def test_remove_bookmark_not_found(client, auth_headers, article):
    response = client.delete(f"/api/bookmarks/{article.id}", headers=auth_headers)

    assert response.status_code == 404
