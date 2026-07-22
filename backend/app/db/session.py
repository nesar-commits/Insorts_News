from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Ensures every model module is imported (and thus registered on Base's
# mapper registry) before any Session is used, so relationship() string
# forward-refs like "Bookmark" resolve correctly.
import app.db.base  # noqa: E402,F401

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
