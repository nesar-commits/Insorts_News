import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


def _register_payload(**overrides):
    payload = {
        "email": "reader@example.com",
        "username": "reader1",
        "password": "correct-horse-battery",
        "full_name": "Test Reader",
    }
    payload.update(overrides)
    return payload


def test_register_returns_token_and_user(client):
    response = client.post("/api/auth/register", json=_register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "reader@example.com"
    assert body["user"]["username"] == "reader1"
    assert "hashed_password" not in body["user"]
    assert body["access_token"]


def test_register_rejects_duplicate_email(client):
    client.post("/api/auth/register", json=_register_payload())

    response = client.post("/api/auth/register", json=_register_payload(username="anotherone"))

    assert response.status_code == 400


def test_register_rejects_duplicate_username(client):
    client.post("/api/auth/register", json=_register_payload())

    response = client.post("/api/auth/register", json=_register_payload(email="someone.else@example.com"))

    assert response.status_code == 400


def test_register_email_is_case_insensitive_for_dupes(client):
    client.post("/api/auth/register", json=_register_payload(email="Reader@Example.com"))

    response = client.post("/api/auth/register", json=_register_payload(email="reader@example.com", username="other"))

    assert response.status_code == 400


def test_login_succeeds_with_correct_credentials(client):
    client.post("/api/auth/register", json=_register_payload())

    response = client.post(
        "/api/auth/login", json={"email": "reader@example.com", "password": "correct-horse-battery"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_fails_with_wrong_password(client):
    client.post("/api/auth/register", json=_register_payload())

    response = client.post("/api/auth/login", json={"email": "reader@example.com", "password": "wrong-password"})

    assert response.status_code == 401


def test_login_fails_for_unknown_email(client):
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "whatever123"})

    assert response.status_code == 401


def test_protected_route_rejects_missing_token(client):
    response = client.get("/api/bookmarks")

    assert response.status_code == 401


def test_protected_route_rejects_garbage_token(client):
    response = client.get("/api/bookmarks", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_register_rejects_password_over_72_bytes_of_multibyte_chars(client):
    # 72 *characters* of 'é' is 144 UTF-8 bytes — passes a character-count
    # check but silently truncates in bcrypt (pinned <4.1.0), so this must
    # be rejected before it ever reaches hash_password.
    response = client.post("/api/auth/register", json=_register_payload(password="é" * 72))

    assert response.status_code == 422


def test_register_accepts_a_72_byte_ascii_password(client):
    response = client.post("/api/auth/register", json=_register_payload(password="x" * 72))

    assert response.status_code == 201


def test_register_rejects_case_variant_of_existing_username(client):
    client.post("/api/auth/register", json=_register_payload(username="janedoe"))

    response = client.post(
        "/api/auth/register", json=_register_payload(email="other@example.com", username="JaneDoe")
    )

    assert response.status_code == 400


def test_db_rejects_case_variant_usernames_even_bypassing_the_app_level_check(db_session):
    # Exercises the actual DB constraint (ix_users_username_lower), not the
    # app-level pre-check in the route — this is what closes the race where
    # two near-simultaneous registrations both pass that pre-check before
    # either commits.
    db_session.add(User(email="a@example.com", username="janedoe", hashed_password="x"))
    db_session.commit()

    db_session.add(User(email="b@example.com", username="JaneDoe", hashed_password="x"))
    with pytest.raises(IntegrityError):
        db_session.commit()
