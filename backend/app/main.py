import logging
import os
import threading
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import articles, auth, bookmarks, categories, push, sources, users
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.article import Article
from app.services.rss_ingest import fetch_and_store_all
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("main")


def _initial_ingest_worker() -> None:
    db = SessionLocal()
    try:
        fetch_and_store_all(db)
    except Exception:
        logger.exception("Initial RSS ingest failed")
    finally:
        db.close()


def _run_migrations_and_initial_ingest() -> None:
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
        if os.path.exists(alembic_ini_path):
            logger.info("Running database migrations on startup (alembic upgrade head)...")
            alembic_cfg = Config(alembic_ini_path)
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations complete.")
    except Exception:
        logger.exception("Alembic upgrade on startup failed, falling back to Base.metadata.create_all")
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            logger.exception("create_all fallback failed")

    # Trigger RSS ingest on startup in a background thread so all categories are immediately up to date
    logger.info("Starting background RSS ingest on startup...")
    threading.Thread(target=_initial_ingest_worker, daemon=True).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations_and_initial_ingest()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(articles.router, prefix=settings.API_V1_PREFIX)
app.include_router(bookmarks.router, prefix=settings.API_V1_PREFIX)
app.include_router(push.router, prefix=settings.API_V1_PREFIX)
app.include_router(sources.router, prefix=settings.API_V1_PREFIX)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
