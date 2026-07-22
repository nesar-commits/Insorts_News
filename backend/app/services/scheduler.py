import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.rss_ingest import fetch_and_store_all

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()


def _run_ingest_job() -> None:
    db = SessionLocal()
    try:
        fetch_and_store_all(db)
    finally:
        db.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        _run_ingest_job,
        "interval",
        minutes=settings.RSS_FETCH_INTERVAL_MINUTES,
        id="rss_ingest",
    )
    scheduler.start()
    logger.info("RSS ingest scheduler started (every %s minutes)", settings.RSS_FETCH_INTERVAL_MINUTES)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
