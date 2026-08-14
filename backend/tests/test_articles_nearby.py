import pytest

from app.api.routes import articles as articles_route
from tests.conftest import make_article, make_source


@pytest.fixture(autouse=True)
def no_dynamic_city_creation(monkeypatch):
    # These tests care about which existing-articles tier gets matched, not
    # the background job that provisions a feed for a brand-new city.
    monkeypatch.setattr(articles_route, "ensure_dynamic_city_source", lambda *a, **k: None)


def _mock_geo(monkeypatch, *, country=None, city=None, ip_country=None, ip_city=None):
    monkeypatch.setattr(articles_route, "get_country_code_from_coords", lambda lat, lon: country)
    monkeypatch.setattr(articles_route, "get_city_from_coords", lambda lat, lon, candidates: city)
    monkeypatch.setattr(articles_route, "get_country_code", lambda request: ip_country)
    monkeypatch.setattr(articles_route, "get_city_from_ip", lambda request, candidates: ip_city)


def test_nearby_false_ignores_location_entirely(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, country="US", city="Ashburn")
    source = make_source(db_session, category, region="GB", city="London")
    make_article(db_session, source, category)

    response = client.get("/api/articles", params={"nearby": False})

    body = response.json()
    assert body["region"] is None
    assert body["city"] is None
    assert body["total"] == 1  # the article is still returned via the unfiltered feed


def test_city_tier_wins_over_region_tier(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, country="GB", city="London")
    city_source = make_source(db_session, category, region="GB", city="London")
    make_article(db_session, city_source, category)
    region_source = make_source(db_session, category, region="GB", city=None)
    make_article(db_session, region_source, category)

    response = client.get("/api/articles", params={"nearby": True, "lat": 51.5, "lon": -0.1})

    body = response.json()
    assert body["city"] == "London"
    assert body["region"] is None
    assert body["total"] == 1


def test_falls_back_to_region_when_city_has_no_articles(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, country="GB", city="Manchester")
    region_source = make_source(db_session, category, region="GB", city=None)
    make_article(db_session, region_source, category)

    response = client.get("/api/articles", params={"nearby": True, "lat": 53.5, "lon": -2.2})

    body = response.json()
    assert body["city"] is None
    assert body["region"] == "GB"
    assert body["total"] == 1


def test_falls_back_to_general_feed_when_nothing_local_matches(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, country="QA", city="Doha")
    other_source = make_source(db_session, category, region="US", city=None)
    make_article(db_session, other_source, category)

    response = client.get("/api/articles", params={"nearby": True})

    body = response.json()
    assert body["city"] is None
    assert body["region"] is None
    assert body["total"] == 1  # general feed still returns the unrelated article


def test_gps_city_takes_priority_over_ip_city(client, db_session, category, monkeypatch):
    # GPS says London; IP (from a US address) says Ashburn — GPS should win
    # since it's the visitor's actual device position, not an ISP guess.
    _mock_geo(monkeypatch, country="GB", city="London", ip_country="US", ip_city="Ashburn")
    london_source = make_source(db_session, category, region="GB", city="London")
    make_article(db_session, london_source, category)
    ashburn_source = make_source(db_session, category, region="US", city="Ashburn")
    make_article(db_session, ashburn_source, category)

    response = client.get("/api/articles", params={"nearby": True, "lat": 51.5, "lon": -0.1})

    assert response.json()["city"] == "London"


def test_ip_fallback_used_when_no_gps_coords_supplied(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, ip_country="US", ip_city="Ashburn")
    source = make_source(db_session, category, region="US", city="Ashburn")
    make_article(db_session, source, category)

    response = client.get("/api/articles", params={"nearby": True})

    assert response.json()["city"] == "Ashburn"


def test_city_and_language_tier_wins_over_city_only(client, db_session, category, monkeypatch):
    _mock_geo(monkeypatch, country="IN", city="Mumbai")
    hindi_source = make_source(db_session, category, region="IN", city="Mumbai", language="hi")
    make_article(db_session, hindi_source, category)
    english_source = make_source(db_session, category, region="IN", city="Mumbai", language="en")
    make_article(db_session, english_source, category)

    response = client.get(
        "/api/articles", params={"nearby": True, "lang": "hi", "lat": 19.07, "lon": 72.87}
    )

    body = response.json()
    assert body["city"] == "Mumbai"
    assert body["language"] == "hi"
    assert body["total"] == 1


def test_invalid_latitude_is_rejected(client):
    response = client.get("/api/articles", params={"nearby": True, "lat": 999, "lon": 0})

    assert response.status_code == 422
