from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_category_published", "category_id", "published_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source: Mapped["Source"] = relationship(back_populates="articles")
    category: Mapped["Category"] = relationship(back_populates="articles")
    bookmarked_by: Mapped[list["Bookmark"]] = relationship(back_populates="article", cascade="all, delete-orphan")
