import pytest


def test_login_success(client, admin_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, admin_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "WrongPassword@1",
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_email(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "ghost@test.com",
        "password": "Ghost@1234",
    })
    assert response.status_code == 401


def test_login_inactive_user(client, db, admin_user):
    admin_user.is_active = False
    db.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    assert response.status_code == 403
    assert "deactivated" in response.json()["detail"]


def test_get_me_returns_current_user(client, admin_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"
    assert response.json()["role"] == "admin"


def test_get_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_refresh_token(client, admin_user):
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    refresh_token = login.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_with_invalid_token(client):
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": "this.is.invalid"
    })
    assert response.status_code == 401