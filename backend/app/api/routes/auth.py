from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email is already registered")
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username is already taken")

    try:
        user = create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username is already taken")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, user=UserRead.model_validate(user))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, user=UserRead.model_validate(user))
