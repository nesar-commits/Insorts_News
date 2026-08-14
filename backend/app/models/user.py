from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# A plain unique constraint on `username` is case-sensitive, but
# crud.user.get_user_by_username's duplicate check is case-insensitive —
# without this, two near-simultaneous registrations for e.g. "test" and
# "Test" can both pass that pre-check (neither exists yet) and both insert
# successfully, since the DB itself never saw them as duplicates. An
# expression index on the lowercased value is enforced by the DB itself and
# closes that race — and it's exactly the form get_user_by_username already
# queries by, so it also speeds up that lookup.
Index("ix_users_username_lower", func.lower(User.username), unique=True)
