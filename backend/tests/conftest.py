from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.article import Article
from app.models.category import Category
from app.models.source import Source


@pytest.fixture()
def db_session():
    # In-memory SQLite, one connection shared via StaticPool so every
    # session in this test sees the same schema/data — a fresh engine per
    # test gives full isolation without needing a real Postgres for tests.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # Not used as a context manager: that would run app.main's lifespan
    # (starts the real APScheduler RSS job against the real DATABASE_URL),
    # which route tests have no need for and shouldn't depend on.
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def category(db_session):
    cat = Category(name="World", slug="world", icon="globe")
    db_session.add(cat)
    db_session.commit()
    return cat


_counter = iter(range(1, 1_000_000))


def make_source(db_session, category, **overrides):
    n = next(_counter)
    defaults = dict(
        name="Test Source",
        feed_url=f"https://example.com/feed/{n}",
        site_url="https://example.com",
        category_id=category.id,
    )
    defaults.update(overrides)
    source = Source(**defaults)
    db_session.add(source)
    db_session.commit()
    return source


def make_article(db_session, source, category, **overrides):
    n = next(_counter)
    defaults = dict(
        title="Test Article",
        summary="A test summary",
        url=f"https://example.com/article/{n}",
        source_id=source.id,
        category_id=category.id,
        published_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    defaults.update(overrides)
    article = Article(**defaults)
    db_session.add(article)
    db_session.commit()
    return article
