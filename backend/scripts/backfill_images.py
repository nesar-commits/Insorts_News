"""One-off backfill: fetch og:image for existing articles ingested before the
RSS feed had no embedded image and the og:image fallback didn't exist yet.

Usage: python -m scripts.backfill_images
"""
from app.db.session import SessionLocal
from app.models.article import Article
from app.services.rss_ingest import _fetch_og_image, _is_valid_image_url


def main() -> None:
    db = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.image_url.is_(None)).all()
        print(f"Found {len(articles)} articles with no image. Fetching og:image...")

        updated = 0
        for i, article in enumerate(articles, start=1):
            image_url = _fetch_og_image(article.url)
            if _is_valid_image_url(image_url):
                article.image_url = image_url
                updated += 1
            if i % 10 == 0:
                db.commit()
                print(f"  {i}/{len(articles)} processed, {updated} updated so far")

        db.commit()
        print(f"Done: {updated}/{len(articles)} articles now have an image.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
