from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription


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
