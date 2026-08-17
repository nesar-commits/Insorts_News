import pytest


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "profile@example.com", "username": "profileuser", "password": "hunter22-battery"},
    )
    login = client.post(
        "/api/auth/login", json={"email": "profile@example.com", "password": "hunter22-battery"}
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_update_full_name(client, auth_headers):
    response = client.patch("/api/users/me", json={"full_name": "New Name"}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"


def test_clear_full_name(client, auth_headers):
    client.patch("/api/users/me", json={"full_name": "Initial Name"}, headers=auth_headers)
    response = client.patch("/api/users/me", json={"full_name": None}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["full_name"] is None


def test_update_username(client, auth_headers):
    response = client.patch("/api/users/me", json={"username": "newname"}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "newname"


def test_update_username_rejects_taken_name(client, auth_headers):
    client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "username": "takenname", "password": "another-battery1"},
    )

    response = client.patch("/api/users/me", json={"username": "takenname"}, headers=auth_headers)

    assert response.status_code == 400


def test_update_username_rejects_case_variant_of_taken_name(client, auth_headers):
    client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "username": "TakenName", "password": "another-battery1"},
    )

    response = client.patch("/api/users/me", json={"username": "takenname"}, headers=auth_headers)

    assert response.status_code == 400


def test_update_profile_requires_auth(client):
    response = client.patch("/api/users/me", json={"full_name": "Nope"})

    assert response.status_code == 401


def test_change_password_succeeds_and_new_password_works(client, auth_headers):
    response = client.post(
        "/api/users/me/change-password",
        json={"current_password": "hunter22-battery", "new_password": "brand-new-battery1"},
        headers=auth_headers,
    )
    assert response.status_code == 204

    old_login = client.post(
        "/api/auth/login", json={"email": "profile@example.com", "password": "hunter22-battery"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/auth/login", json={"email": "profile@example.com", "password": "brand-new-battery1"}
    )
    assert new_login.status_code == 200


def test_change_password_rejects_wrong_current_password(client, auth_headers):
    response = client.post(
        "/api/users/me/change-password",
        json={"current_password": "wrong-password", "new_password": "brand-new-battery1"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_change_password_rejects_password_over_72_bytes(client, auth_headers):
    response = client.post(
        "/api/users/me/change-password",
        json={"current_password": "hunter22-battery", "new_password": "é" * 72},
        headers=auth_headers,
    )
    assert response.status_code == 422
