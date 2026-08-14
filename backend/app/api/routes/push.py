from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.push_subscription import (
    delete_subscription,
    get_subscription_by_endpoint_and_keys,
    set_subscription_categories,
    upsert_subscription,
)
from app.db.session import get_db
from app.schemas.push import PushCategoryUpdate, PushSubscriptionCreate, VapidPublicKey

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key", response_model=VapidPublicKey)
def vapid_public_key():
    return VapidPublicKey(key=settings.VAPID_PUBLIC_KEY)


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe(subscription: PushSubscriptionCreate, db: Session = Depends(get_db)):
    sub = upsert_subscription(db, subscription.endpoint, subscription.keys.p256dh, subscription.keys.auth)
    if subscription.category_ids is not None:
        set_subscription_categories(db, sub.id, subscription.category_ids)


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(subscription: PushSubscriptionCreate, db: Session = Depends(get_db)):
    delete_subscription(db, subscription.endpoint, subscription.keys.p256dh, subscription.keys.auth)


@router.put("/categories", status_code=status.HTTP_204_NO_CONTENT)
def update_push_categories(payload: PushCategoryUpdate, db: Session = Depends(get_db)):
    sub = get_subscription_by_endpoint_and_keys(db, payload.endpoint, payload.keys.p256dh, payload.keys.auth)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    set_subscription_categories(db, sub.id, payload.category_ids)
