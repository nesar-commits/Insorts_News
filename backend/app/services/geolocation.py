import ipaddress
import logging
from functools import lru_cache

import httpx
from fastapi import Request

logger = logging.getLogger("geolocation")


def _client_ip(request: Request) -> str | None:
    # Render/Vercel and most reverse proxies set this; the left-most entry is
    # the original client. Fall back to the raw connection address (e.g. in
    # local dev, where there's no proxy in front of uvicorn).
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def _is_public_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved)


@lru_cache(maxsize=2048)
def _lookup_ip_location(ip: str) -> dict | None:
    try:
        response = httpx.get(
            f"http://ip-api.com/json/{ip}", params={"fields": "status,countryCode,city"}, timeout=2.0
        )
        data = response.json()
        if data.get("status") == "success":
            return data
    except Exception:
        logger.warning("IP geolocation lookup failed for %s", ip, exc_info=True)
    return None


def get_country_code(request: Request) -> str | None:
    """Best-effort country code for "nearby news" — returns None (meaning
    "show the general feed instead") for local/private IPs or any lookup
    failure, never raises.
    """
    ip = _client_ip(request)
    if not ip or not _is_public_ip(ip):
        return None
    data = _lookup_ip_location(ip)
    return data.get("countryCode") if data else None


def get_city_from_ip(request: Request, candidate_cities: list[str]) -> str | None:
    """IP-based city guess — lower confidence than GPS (ISP-registered
    location, not the device's actual position), used only when the browser
    didn't grant location permission at all.

    Prefers an exact match against `candidate_cities` (our verified, curated
    sources) for correct canonical naming, but falls back to whatever city
    name the IP lookup itself reports — this is what lets a location with no
    curated source still get real local news, via the dynamic city feed (see
    app/services/dynamic_city.py), instead of being limited to a fixed list.
    """
    ip = _client_ip(request)
    if not ip or not _is_public_ip(ip):
        return None
    data = _lookup_ip_location(ip)
    ip_city = (data or {}).get("city")
    if not ip_city:
        return None
    for candidate in candidate_cities:
        if candidate.lower() == ip_city.lower():
            return candidate
    return ip_city


@lru_cache(maxsize=2048)
def _reverse_geocode(lat_rounded: float, lon_rounded: float) -> dict | None:
    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "jsonv2",
                "lat": lat_rounded,
                "lon": lon_rounded,
                "zoom": 10,
                "accept-language": "en",
            },
            headers={"User-Agent": "InsortsNews/1.0 (nearby-news feature)"},
            timeout=3.0,
        )
        return response.json()
    except Exception:
        logger.warning("Reverse geocode failed for (%s, %s)", lat_rounded, lon_rounded, exc_info=True)
        return None


def get_country_code_from_coords(lat: float, lon: float) -> str | None:
    """GPS-precise alternative to IP geolocation — the caller (a browser
    that got the user's permission) supplies real coordinates, so this works
    correctly for rural/remote areas where an ISP's registered IP location
    is often a distant city or even the wrong country entirely.

    Rounded to ~1km precision before caching/lookup — country-level accuracy
    doesn't need more, and it keeps the reverse-geocoding cache useful across
    nearby requests instead of missing on every slightly-different reading.
    """
    data = _reverse_geocode(round(lat, 2), round(lon, 2))
    if not data:
        return None
    code = data.get("address", {}).get("country_code")
    return code.upper() if code else None


def get_city_from_coords(lat: float, lon: float, candidate_cities: list[str]) -> str | None:
    """GPS-precise city detection — works for any location on Earth, not
    just a curated list.

    First checks the full `display_name` string against `candidate_cities`
    (our verified, curated sources): Nominatim's `address.city` field reports
    inconsistent granularity across cities/countries — a query inside London
    returns the borough ("City of Westminster"), not "London" — so matching
    against the broader display_name hierarchy gets the canonical name right
    for cities we already have a real local source for.

    Falls back to whatever raw city/town name Nominatim reports for anywhere
    else — this is what lets a location with no curated source still get
    real local news, via the dynamic city feed (see dynamic_city.py), rather
    than being limited to the curated list.
    """
    data = _reverse_geocode(round(lat, 2), round(lon, 2))
    if not data:
        return None
    display_name = (data.get("display_name") or "").lower()
    for candidate in candidate_cities:
        if display_name and candidate.lower() in display_name:
            return candidate
    address = data.get("address", {})
    return address.get("city") or address.get("town") or address.get("municipality") or address.get("city_district")
