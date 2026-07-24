from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    feed_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    site_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    # ISO 3166-1 alpha-2 country code this source primarily covers, or None
    # if it isn't tied to one — powers "nearby news" (see geolocation.py).
    region: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # ISO 639-1 language code the source is actually published in — refines
    # "nearby news" by the visitor's browser language preference.
    language: Mapped[str | None] = mapped_column(String(3), nullable=True)
    # City this source covers, if it's a local (not national) outlet — the
    # highest-priority match tier in "nearby news", above region/language.
    # Indexed: get_distinct_cities() and every city lookup scan this column
    # on every nearby=true request, and dynamically-created cities accumulate
    # over time with no eviction.
    city: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    category: Mapped["Category"] = relationship(back_populates="sources")
    articles: Mapped[list["Article"]] = relationship(back_populates="source")
