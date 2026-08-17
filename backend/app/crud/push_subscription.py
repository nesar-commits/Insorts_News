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
    sub = get_subscription_by_endpoint_and_keys(db, endpoint, p256dh, auth)
    if sub:
        db.query(PushSubscriptionCategory).filter(
            PushSubscriptionCategory.subscription_id == sub.id
        ).delete()
        db.delete(sub)
        db.commit()


def get_all_subscriptions(db: Session) -> list[PushSubscription]:
    return db.query(PushSubscription).all()


def delete_subscription_by_id(db: Session, subscription_id: int) -> None:
    db.query(PushSubscriptionCategory).filter(
        PushSubscriptionCategory.subscription_id == subscription_id
    ).delete()
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


def set_subscription_categories(db: Session, subscription_id: int, category_ids: list[int] | None) -> None:
    """category_ids=None resets to "every category" (receives_all_categories
    True, no filter rows). A list — including an empty one — sets an
    explicit filter: [] means "opted out of every category", which is
    stored as receives_all_categories=False with zero rows, distinct from
    the None/default state that also has zero rows.
    """
    db.query(PushSubscriptionCategory).filter(
        PushSubscriptionCategory.subscription_id == subscription_id
    ).delete()
    db.query(PushSubscription).filter(PushSubscription.id == subscription_id).update(
        {"receives_all_categories": category_ids is None}
    )
    if category_ids:
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
    """Subscriptions with receives_all_categories True (the default for
    anyone who never set a preference) get every send — so a filtered
    send has to include both those AND the ones that specifically opted
    into `category_id`, not just the latter. Subscriptions that
    explicitly opted out of everything (receives_all_categories False,
    no rows) get neither.
    """
    if category_id is None:
        return db.query(PushSubscription).all()

    no_filter_ids = {
        row[0]
        for row in db.query(PushSubscription.id)
        .filter(PushSubscription.receives_all_categories.is_(True))
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
