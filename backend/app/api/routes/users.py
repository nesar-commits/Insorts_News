from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import verify_password
from app.crud.article import get_category, get_source
from app.crud.mute import (
    get_muted_category_ids,
    get_muted_source_ids,
    mute_category,
    mute_source,
    unmute_category,
    unmute_source,
)
from app.crud.user import get_user_by_username, set_password, update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.preferences import MutedPreferences
from app.schemas.user import PasswordChange, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_in.username is not None:
        existing = get_user_by_username(db, user_in.username)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username is already taken")

    try:
        return update_user(db, current_user, user_in)
    except IntegrityError:
        # Closes the same TOCTOU race the pre-check above can't: two
        # near-simultaneous requests both changing to the same new
        # username. The DB's case-insensitive unique index is the real
        # guard; the pre-check is just a friendlier error for the common case.
        db.rollback()
        raise HTTPException(status_code=400, detail="Username is already taken")


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    set_password(db, current_user, payload.new_password)


@router.get("/me/muted", response_model=MutedPreferences)
def get_muted_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MutedPreferences(
        muted_source_ids=sorted(get_muted_source_ids(db, current_user.id)),
        muted_category_ids=sorted(get_muted_category_ids(db, current_user.id)),
    )


@router.post("/me/muted-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def mute_a_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not get_source(db, source_id):
        raise HTTPException(status_code=404, detail="Source not found")
    mute_source(db, current_user.id, source_id)


@router.delete("/me/muted-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def unmute_a_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unmute_source(db, current_user.id, source_id)


@router.post("/me/muted-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def mute_a_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not get_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    mute_category(db, current_user.id, category_id)


@router.delete("/me/muted-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def unmute_a_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unmute_category(db, current_user.id, category_id)
