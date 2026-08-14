from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _check_password_byte_length(value: str) -> str:
    # bcrypt (pinned <4.1.0 — see requirements.txt) truncates the *byte*
    # representation at 72 with no error, but a character-count max_length
    # wouldn't catch that — a password of 72 multi-byte characters (e.g.
    # non-Latin scripts, emoji) would pass yet get silently truncated at
    # hash time, weakening it without the user ever knowing.
    if len(value.encode("utf-8")) > 72:
        raise ValueError("password must be at most 72 bytes")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, max_length=120)

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, value: str) -> str:
        return _check_password_byte_length(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=120)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_byte_length(cls, value: str) -> str:
        return _check_password_byte_length(value)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str | None = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
