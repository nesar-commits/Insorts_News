from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Device/browser-level, not tied to a user account — notification opt-in
    # shouldn't require being logged in.
    endpoint: Mapped[str] = mapped_column(String(1000), unique=True, index=True, nullable=False)
    p256dh: Mapped[str] = mapped_column(String(512), nullable=False)
    auth: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
