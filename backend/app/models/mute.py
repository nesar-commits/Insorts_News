from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MutedSource(Base):
    """A user has said "not interested" in a specific source — its
    articles are excluded from that user's feed and trending list.
    """

    __tablename__ = "muted_sources"
    __table_args__ = (UniqueConstraint("user_id", "source_id", name="uq_user_muted_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="muted_sources")


class MutedCategory(Base):
    """Same as MutedSource, but for an entire category."""

    __tablename__ = "muted_categories"
    __table_args__ = (UniqueConstraint("user_id", "category_id", name="uq_user_muted_category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="muted_categories")
