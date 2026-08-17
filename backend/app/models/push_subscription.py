from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    # True (the default) means "no category preference set — send every
    # category", matching pre-existing behavior for anyone who never
    # touches this preference. False + zero category_filters rows means
    # the subscriber explicitly opted out of every category, which is a
    # distinct state from the default and must NOT match any send —
    # without this flag, both states are indistinguishable from "zero
    # rows" and an explicit opt-out-of-everything silently turns back
    # into opt-in-to-everything.
    receives_all_categories: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    category_filters: Mapped[list["PushSubscriptionCategory"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


class PushSubscriptionCategory(Base):
    """A category this subscription has opted into for breaking-news
    pushes. Only meaningful when the parent subscription's
    receives_all_categories is False — see that field's docstring.
    """

    __tablename__ = "push_subscription_categories"
    __table_args__ = (
        UniqueConstraint("subscription_id", "category_id", name="uq_subscription_category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("push_subscriptions.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    subscription: Mapped["PushSubscription"] = relationship(back_populates="category_filters")
