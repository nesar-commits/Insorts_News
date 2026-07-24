from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.push_subscription import delete_subscription, upsert_subscription
from app.db.session import get_db
from app.schemas.push import PushSubscriptionCreate, VapidPublicKey

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key", response_model=VapidPublicKey)
def vapid_public_key():
    return VapidPublicKey(key=settings.VAPID_PUBLIC_KEY)


@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe(subscription: PushSubscriptionCreate, db: Session = Depends(get_db)):
    upsert_subscription(db, subscription.endpoint, subscription.keys.p256dh, subscription.keys.auth)


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(subscription: PushSubscriptionCreate, db: Session = Depends(get_db)):
    delete_subscription(db, subscription.endpoint)
