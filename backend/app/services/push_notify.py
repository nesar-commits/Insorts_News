import json
import logging

import requests
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.push_subscription import delete_subscription_by_id, get_all_subscriptions

logger = logging.getLogger("push_notify")


def send_push_to_all(db: Session, title: str, body: str, url: str = "/") -> int:
    """Sends one push notification to every subscribed device. Prunes
    subscriptions the push service reports as gone (uninstalled app, expired
    endpoint) instead of retrying them forever. Returns count actually sent.
    """
    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured — skipping push notification")
        return 0

    payload = json.dumps({"title": title, "body": body, "url": url})
    sent = 0
    for sub in get_all_subscriptions(db):
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
            sent += 1
        except WebPushException as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code in (404, 410):
                delete_subscription_by_id(db, sub.id)
            else:
                logger.warning("Push failed for subscription %s: %s", sub.id, exc)
        except requests.exceptions.RequestException as exc:
            # webpush() only wraps a non-2xx *response* in WebPushException —
            # a transport-level failure (DNS failure, connection refused,
            # timeout, TLS error) raises straight from the underlying
            # `requests` call instead. Without this, one subscriber with a
            # dead endpoint would abort the loop and silently skip every
            # subscriber after it in this batch.
            logger.warning("Push transport error for subscription %s: %s", sub.id, exc)
    return sent
