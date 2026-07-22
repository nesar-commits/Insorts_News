"""Seed categories/sources and run an initial RSS fetch.

Usage: python -m scripts.seed
"""
from app.db.session import SessionLocal
from app.services.rss_ingest import fetch_and_store_all


def main() -> None:
    db = SessionLocal()
    try:
        new_count = fetch_and_store_all(db)
        print(f"Seed complete: {new_count} new articles ingested.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
