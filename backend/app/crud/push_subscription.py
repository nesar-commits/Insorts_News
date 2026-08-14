from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription, PushSubscriptionCategory


def upsert_subscription(db: Session, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
    if existing:
        existing.p256dh = p256dh
        existing.auth = auth
        db.commit()
        db.refresh(existing)
        return existing

    new_subscription = PushSubscription(endpoint=endpoint, p256dh=p256dh, auth=auth)
    db.add(new_subscription)
    try:
        db.commit()
    except IntegrityError:
        # Two near-simultaneous subscribe calls for the same brand-new
        # endpoint raced each other — the other one won, so just update its
        # row with these (possibly refreshed) keys instead of erroring.
        db.rollback()
        existing = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
        existing.p256dh = p256dh
        existing.auth = auth
        db.commit()
        db.refresh(existing)
        return existing
    db.refresh(new_subscription)
    return new_subscription


def delete_subscription(db: Session, endpoint: str, p256dh: str, auth: str) -> None:
    # Subscriptions aren't tied to an account, so the keys act as the only
    # proof of ownership — without checking them, anyone who merely obtained
    # someone else's endpoint string (logs, a debugging tool) could silently
    # unsubscribe that person's device.
    db.query(PushSubscription).filter(
        PushSubscription.endpoint == endpoint,
        PushSubscription.p256dh == p256dh,
        PushSubscription.auth == auth,
    ).delete()
    db.commit()


def get_all_subscriptions(db: Session) -> list[PushSubscription]:
    return db.query(PushSubscription).all()


def delete_subscription_by_id(db: Session, subscription_id: int) -> None:
    db.query(PushSubscription).filter(PushSubscription.id == subscription_id).delete()
    db.commit()


def get_subscription_by_endpoint_and_keys(
    db: Session, endpoint: str, p256dh: str, auth: str
) -> PushSubscription | None:
    # Same ownership proof as delete_subscription — a subscription isn't
    # tied to a user account, so its own keys are the only thing that
    # should let a caller change what it receives.
    return (
        db.query(PushSubscription)
        .filter(
            PushSubscription.endpoint == endpoint,
            PushSubscription.p256dh == p256dh,
            PushSubscription.auth == auth,
        )
        .first()
    )


def set_subscription_categories(db: Session, subscription_id: int, category_ids: list[int]) -> None:
    db.query(PushSubscriptionCategory).filter(
        PushSubscriptionCategory.subscription_id == subscription_id
    ).delete()
    for category_id in set(category_ids):
        db.add(PushSubscriptionCategory(subscription_id=subscription_id, category_id=category_id))
    db.commit()


def get_subscription_category_ids(db: Session, subscription_id: int) -> set[int]:
    rows = (
        db.query(PushSubscriptionCategory.category_id)
        .filter(PushSubscriptionCategory.subscription_id == subscription_id)
        .all()
    )
    return {row[0] for row in rows}


def get_subscriptions_for_category(db: Session, category_id: int | None) -> list[PushSubscription]:
    """No category filters at all on a subscription means "every
    category" — so a filtered send has to include both the subscriptions
    that specifically opted into `category_id` AND the ones with no
    filters set, not just the former.
    """
    if category_id is None:
        return db.query(PushSubscription).all()

    no_filter_ids = {
        row[0]
        for row in db.query(PushSubscription.id)
        .outerjoin(PushSubscriptionCategory)
        .filter(PushSubscriptionCategory.id.is_(None))
        .all()
    }
    matching_ids = {
        row[0]
        for row in db.query(PushSubscriptionCategory.subscription_id)
        .filter(PushSubscriptionCategory.category_id == category_id)
        .all()
    }
    ids = no_filter_ids | matching_ids
    if not ids:
        return []
    return db.query(PushSubscription).filter(PushSubscription.id.in_(ids)).all()
