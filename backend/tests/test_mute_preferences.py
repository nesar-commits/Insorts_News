import pytest

from tests.conftest import make_article, make_source


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "muter@example.com", "username": "muter", "password": "hunter22-battery"},
    )
    login = client.post("/api/auth/login", json={"email": "muter@example.com", "password": "hunter22-battery"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_list_sources(client, db_session, category):
    make_source(db_session, category, name="Alpha News")

    response = client.get("/api/sources")

    assert response.status_code == 200
    assert any(s["name"] == "Alpha News" for s in response.json())


def test_mute_and_unmute_source(client, db_session, category, auth_headers):
    source = make_source(db_session, category)

    mute = client.post(f"/api/users/me/muted-sources/{source.id}", headers=auth_headers)
    assert mute.status_code == 204

    prefs = client.get("/api/users/me/muted", headers=auth_headers)
    assert prefs.json()["muted_source_ids"] == [source.id]

    unmute = client.delete(f"/api/users/me/muted-sources/{source.id}", headers=auth_headers)
    assert unmute.status_code == 204

    prefs_after = client.get("/api/users/me/muted", headers=auth_headers)
    assert prefs_after.json()["muted_source_ids"] == []


def test_mute_unknown_source_404s(client, auth_headers):
    response = client.post("/api/users/me/muted-sources/999999", headers=auth_headers)

    assert response.status_code == 404


def test_mute_source_is_idempotent(client, db_session, category, auth_headers):
    source = make_source(db_session, category)

    first = client.post(f"/api/users/me/muted-sources/{source.id}", headers=auth_headers)
    second = client.post(f"/api/users/me/muted-sources/{source.id}", headers=auth_headers)

    assert first.status_code == 204
    assert second.status_code == 204
    prefs = client.get("/api/users/me/muted", headers=auth_headers)
    assert prefs.json()["muted_source_ids"] == [source.id]


def test_mute_category(client, db_session, category, auth_headers):
    mute = client.post(f"/api/users/me/muted-categories/{category.id}", headers=auth_headers)
    assert mute.status_code == 204

    prefs = client.get("/api/users/me/muted", headers=auth_headers)
    assert prefs.json()["muted_category_ids"] == [category.id]


def test_muted_source_is_excluded_from_feed(client, db_session, category, auth_headers):
    muted_source = make_source(db_session, category)
    other_source = make_source(db_session, category)
    make_article(db_session, muted_source, category, title="Hidden article")
    make_article(db_session, other_source, category, title="Visible article")

    client.post(f"/api/users/me/muted-sources/{muted_source.id}", headers=auth_headers)

    response = client.get("/api/articles", headers=auth_headers)
    titles = [a["title"] for a in response.json()["items"]]
    assert "Hidden article" not in titles
    assert "Visible article" in titles


def test_muted_category_is_excluded_from_feed(client, db_session, category, auth_headers):
    source = make_source(db_session, category)
    make_article(db_session, source, category, title="From muted category")

    client.post(f"/api/users/me/muted-categories/{category.id}", headers=auth_headers)

    response = client.get("/api/articles", headers=auth_headers)
    titles = [a["title"] for a in response.json()["items"]]
    assert "From muted category" not in titles


def test_muting_has_no_effect_for_anonymous_requests(client, db_session, category):
    source = make_source(db_session, category)
    make_article(db_session, source, category, title="Anon visible")

    response = client.get("/api/articles")
    titles = [a["title"] for a in response.json()["items"]]
    assert "Anon visible" in titles
