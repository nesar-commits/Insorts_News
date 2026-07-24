from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.crud.article import (
    city_and_language_has_articles,
    city_has_articles,
    get_article,
    get_articles,
    get_bookmarked_article_ids,
    get_distinct_cities,
    region_and_language_has_articles,
    region_has_articles,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.article import ArticleRead, PaginatedArticles
from app.services.dynamic_city import ensure_dynamic_city_source
from app.services.geolocation import (
    get_city_from_coords,
    get_city_from_ip,
    get_country_code,
    get_country_code_from_coords,
)

router = APIRouter(prefix="/articles", tags=["articles"])


def _to_article_read(article, bookmarked_ids: set[int]) -> ArticleRead:
    data = ArticleRead.model_validate(article)
    data.is_bookmarked = article.id in bookmarked_ids
    return data


def _decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        published_at_raw, id_raw = cursor.rsplit("_", 1)
        return datetime.fromisoformat(published_at_raw), int(id_raw)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid pagination cursor")


def _encode_cursor(published_at: datetime, article_id: int) -> str:
    return f"{published_at.isoformat()}_{article_id}"


@router.get("", response_model=PaginatedArticles)
def list_articles(
    request: Request,
    background_tasks: BackgroundTasks,
    cursor: str | None = Query(None, description="Opaque cursor from a previous response's next_cursor"),
    page_size: int = Query(20, ge=1, le=50),
    category: str | None = Query(None, description="Category slug, or omit for all"),
    search: str | None = Query(None, min_length=1, max_length=200),
    nearby: bool = Query(False, description="Prefer articles from the visitor's detected country"),
    lat: float | None = Query(None, ge=-90, le=90, description="Browser-supplied GPS latitude"),
    lon: float | None = Query(None, ge=-180, le=180, description="Browser-supplied GPS longitude"),
    lang: str | None = Query(None, min_length=2, max_length=3, description="Visitor's preferred language code"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    decoded_cursor = _decode_cursor(cursor) if cursor else None

    matched_city = None
    matched_region = None
    matched_language = None
    if nearby:
        has_gps = lat is not None and lon is not None

        # GPS (from an explicit browser permission grant) beats IP geolocation
        # — an ISP's registered IP location is often a distant city for rural
        # connections, sometimes even the wrong country.
        detected_country = get_country_code_from_coords(lat, lon) if has_gps else None
        if not detected_country:
            detected_country = get_country_code(request)

        candidate_cities = get_distinct_cities(db)
        detected_city = get_city_from_coords(lat, lon, candidate_cities) if has_gps else None
        if not detected_city:
            detected_city = get_city_from_ip(request, candidate_cities)

        # Five-tier fallback, most specific first — never show an empty feed
        # just because one tier had nothing to match:
        #   city+language > city > region+language > region > general
        if detected_city and lang and city_and_language_has_articles(db, detected_city, lang):
            matched_city = detected_city
            matched_language = lang
        elif detected_city and city_has_articles(db, detected_city):
            matched_city = detected_city
        elif detected_country and lang and region_and_language_has_articles(db, detected_country, lang):
            matched_region = detected_country
            matched_language = lang
        elif detected_country and region_has_articles(db, detected_country):
            matched_region = detected_country

        if detected_city and not matched_city:
            # First-ever visit from this city (or one that's never actually
            # gained coverage) — set up a real local feed for it in the
            # background, so it "just works" on the next visit instead of
            # making this one wait on a live fetch. This request still falls
            # through to the region/general tiers above like normal.
            background_tasks.add_task(ensure_dynamic_city_source, detected_city, detected_country)

    items, total = get_articles(
        db,
        page_size=page_size,
        category_slug=category,
        search=search,
        cursor=decoded_cursor,
        region=matched_region,
        language=matched_language,
        city=matched_city,
    )

    bookmarked_ids = (
        get_bookmarked_article_ids(db, current_user.id, [a.id for a in items]) if current_user else set()
    )

    next_cursor = _encode_cursor(items[-1].published_at, items[-1].id) if len(items) == page_size else None

    return PaginatedArticles(
        items=[_to_article_read(a, bookmarked_ids) for a in items],
        total=total,
        next_cursor=next_cursor,
        region=matched_region,
        language=matched_language,
        city=matched_city,
    )


@router.get("/trending", response_model=list[ArticleRead])
def trending_articles(
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    items, _ = get_articles(db, page=1, page_size=limit)
    bookmarked_ids = (
        get_bookmarked_article_ids(db, current_user.id, [a.id for a in items]) if current_user else set()
    )
    return [_to_article_read(a, bookmarked_ids) for a in items]


@router.get("/{article_id}", response_model=ArticleRead)
def read_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    bookmarked_ids = get_bookmarked_article_ids(db, current_user.id, [article.id]) if current_user else set()
    return _to_article_read(article, bookmarked_ids)
