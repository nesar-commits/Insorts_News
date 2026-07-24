from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription


def upsert_subscription(db: Session, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
    if existing:
        existing.p256dh = p256dh
        existing.auth = auth
    else:
        existing = PushSubscription(endpoint=endpoint, p256dh=p256dh, auth=auth)
        db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing


def delete_subscription(db: Session, endpoint: str) -> None:
    db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).delete()
    db.commit()


def get_all_subscriptions(db: Session) -> list[PushSubscription]:
    return db.query(PushSubscription).all()


def delete_subscription_by_id(db: Session, subscription_id: int) -> None:
    db.query(PushSubscription).filter(PushSubscription.id == subscription_id).delete()
    db.commit()
