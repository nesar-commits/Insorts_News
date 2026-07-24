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
def _lookup_country_code(ip: str) -> str | None:
    try:
        response = httpx.get(
            f"http://ip-api.com/json/{ip}", params={"fields": "status,countryCode"}, timeout=2.0
        )
        data = response.json()
        if data.get("status") == "success":
            return data.get("countryCode")
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
    return _lookup_country_code(ip)


@lru_cache(maxsize=2048)
def _reverse_geocode(lat_rounded: float, lon_rounded: float) -> str | None:
    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"format": "jsonv2", "lat": lat_rounded, "lon": lon_rounded, "zoom": 3},
            headers={"User-Agent": "InsortsNews/1.0 (nearby-news feature)"},
            timeout=3.0,
        )
        data = response.json()
        return data.get("address", {}).get("country_code", "").upper() or None
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
    return _reverse_geocode(round(lat, 2), round(lon, 2))
