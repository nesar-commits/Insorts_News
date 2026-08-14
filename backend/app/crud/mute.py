from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.mute import MutedCategory, MutedSource


def mute_source(db: Session, user_id: int, source_id: int) -> None:
    db.add(MutedSource(user_id=user_id, source_id=source_id))
    try:
        db.commit()
    except IntegrityError:
        # Already muted (double-click, duplicate request) — idempotent.
        db.rollback()


def unmute_source(db: Session, user_id: int, source_id: int) -> None:
    db.query(MutedSource).filter(
        MutedSource.user_id == user_id, MutedSource.source_id == source_id
    ).delete()
    db.commit()


def get_muted_source_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(MutedSource.source_id).filter(MutedSource.user_id == user_id).all()
    return {row[0] for row in rows}


def mute_category(db: Session, user_id: int, category_id: int) -> None:
    db.add(MutedCategory(user_id=user_id, category_id=category_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def unmute_category(db: Session, user_id: int, category_id: int) -> None:
    db.query(MutedCategory).filter(
        MutedCategory.user_id == user_id, MutedCategory.category_id == category_id
    ).delete()
    db.commit()


def get_muted_category_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(MutedCategory.category_id).filter(MutedCategory.user_id == user_id).all()
    return {row[0] for row in rows}
