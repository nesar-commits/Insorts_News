from unittest.mock import MagicMock

import pytest

from app.services import geolocation


class DummyRequest:
    def __init__(self, headers=None, client_host=None):
        self.headers = headers or {}
        self.client = MagicMock(host=client_host) if client_host else None


@pytest.fixture(autouse=True)
def clear_lookup_caches():
    # These are process-wide lru_caches; a value cached by an earlier test
    # would make a later test's mocked httpx/nominatim call never fire.
    geolocation._lookup_ip_location.cache_clear()
    geolocation._reverse_geocode.cache_clear()
    yield
    geolocation._lookup_ip_location.cache_clear()
    geolocation._reverse_geocode.cache_clear()


def test_client_ip_prefers_x_forwarded_for_leftmost_entry():
    request = DummyRequest(headers={"x-forwarded-for": "1.2.3.4, 5.6.7.8"}, client_host="10.0.0.1")

    assert geolocation._client_ip(request) == "1.2.3.4"


def test_client_ip_falls_back_to_socket_when_no_header():
    request = DummyRequest(client_host="203.0.113.5")

    assert geolocation._client_ip(request) == "203.0.113.5"


def test_client_ip_none_when_neither_present():
    request = DummyRequest()

    assert geolocation._client_ip(request) is None


@pytest.mark.parametrize(
    "ip",
    ["10.0.0.1", "192.168.1.1", "127.0.0.1", "169.254.1.1", "not-an-ip", ""],
)
def test_private_reserved_and_malformed_ips_are_rejected(ip):
    assert geolocation._is_public_ip(ip) is False


def test_public_ip_is_accepted():
    assert geolocation._is_public_ip("8.8.8.8") is True


def test_get_country_code_returns_none_for_private_ip():
    request = DummyRequest(client_host="192.168.0.5")

    assert geolocation.get_country_code(request) is None


def test_get_country_code_returns_none_when_lookup_fails(monkeypatch):
    request = DummyRequest(client_host="8.8.8.8")
    monkeypatch.setattr(geolocation, "_lookup_ip_location", lambda ip: None)

    assert geolocation.get_country_code(request) is None


def test_get_country_code_returns_code_on_success(monkeypatch):
    request = DummyRequest(client_host="8.8.8.8")
    monkeypatch.setattr(
        geolocation, "_lookup_ip_location", lambda ip: {"status": "success", "countryCode": "US", "city": "Ashburn"}
    )

    assert geolocation.get_country_code(request) == "US"


def test_get_city_from_ip_returns_none_for_private_ip():
    request = DummyRequest(client_host="10.1.1.1")

    assert geolocation.get_city_from_ip(request, ["London"]) is None


def test_get_city_from_ip_prefers_canonical_candidate_name_case_insensitively(monkeypatch):
    request = DummyRequest(client_host="8.8.8.8")
    monkeypatch.setattr(geolocation, "_lookup_ip_location", lambda ip: {"status": "success", "city": "LONDON"})

    assert geolocation.get_city_from_ip(request, ["London", "Paris"]) == "London"


def test_get_city_from_ip_falls_back_to_raw_city_when_no_candidate_matches(monkeypatch):
    request = DummyRequest(client_host="8.8.8.8")
    monkeypatch.setattr(geolocation, "_lookup_ip_location", lambda ip: {"status": "success", "city": "Ashburn"})

    assert geolocation.get_city_from_ip(request, ["London", "Paris"]) == "Ashburn"


def test_get_city_from_ip_returns_none_when_lookup_has_no_city(monkeypatch):
    request = DummyRequest(client_host="8.8.8.8")
    monkeypatch.setattr(geolocation, "_lookup_ip_location", lambda ip: {"status": "success"})

    assert geolocation.get_city_from_ip(request, ["London"]) is None


def test_get_country_code_from_coords_returns_none_when_geocode_fails(monkeypatch):
    monkeypatch.setattr(geolocation, "_reverse_geocode", lambda lat, lon: None)

    assert geolocation.get_country_code_from_coords(51.5, -0.1) is None


def test_get_country_code_from_coords_uppercases_country_code(monkeypatch):
    monkeypatch.setattr(geolocation, "_reverse_geocode", lambda lat, lon: {"address": {"country_code": "gb"}})

    assert geolocation.get_country_code_from_coords(51.5, -0.1) == "GB"


def test_get_city_from_coords_matches_against_display_name_hierarchy(monkeypatch):
    # Nominatim's address.city for a London query can be a borough
    # ("City of Westminster") rather than "London" itself — the canonical
    # match has to come from the broader display_name, not address.city.
    monkeypatch.setattr(
        geolocation,
        "_reverse_geocode",
        lambda lat, lon: {
            "display_name": "10 Downing Street, City of Westminster, London, England, United Kingdom",
            "address": {"city": "City of Westminster"},
        },
    )

    assert geolocation.get_city_from_coords(51.5, -0.1, ["London", "Paris"]) == "London"


def test_get_city_from_coords_falls_back_to_raw_address_fields(monkeypatch):
    monkeypatch.setattr(
        geolocation,
        "_reverse_geocode",
        lambda lat, lon: {
            "display_name": "Some Village, Somewhere",
            "address": {"town": "Some Village"},
        },
    )

    assert geolocation.get_city_from_coords(51.5, -0.1, ["London", "Paris"]) == "Some Village"


def test_get_city_from_coords_returns_none_when_geocode_fails(monkeypatch):
    monkeypatch.setattr(geolocation, "_reverse_geocode", lambda lat, lon: None)

    assert geolocation.get_city_from_coords(51.5, -0.1, ["London"]) is None
