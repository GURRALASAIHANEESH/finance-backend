import pytest


def test_admin_can_create_user(client, admin_token):
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "New Analyst",
            "email": "newanalyst@test.com",
            "password": "Analyst@9999",
            "role": "analyst",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newanalyst@test.com"
    assert response.json()["role"] == "analyst"


def test_analyst_cannot_create_user(client, analyst_token):
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "Should Fail",
            "email": "fail@test.com",
            "password": "Fail@1234",
            "role": "viewer",
        },
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403


def test_viewer_cannot_create_user(client, viewer_token):
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "Should Fail",
            "email": "fail@test.com",
            "password": "Fail@1234",
            "role": "viewer",
        },
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


def test_duplicate_email_rejected(client, admin_token, admin_user):
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "Duplicate",
            "email": "admin@test.com",
            "password": "Admin@9999",
            "role": "viewer",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409


def test_weak_password_rejected(client, admin_token):
    response = client.post(
        "/api/v1/users/",
        json={
            "name": "Weak Pass",
            "email": "weak@test.com",
            "password": "password",
            "role": "viewer",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


def test_admin_can_list_users(client, admin_token, admin_user):
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "results" in response.json()
    assert response.json()["total"] >= 1


def test_admin_can_update_user_role(client, admin_token, viewer_user):
    response = client.patch(
        f"/api/v1/users/{viewer_user.id}",
        json={"role": "analyst"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "analyst"


def test_admin_cannot_delete_themselves(client, admin_token, admin_user):
    response = client.delete(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "own account" in response.json()["detail"]


def test_delete_nonexistent_user(client, admin_token):
    response = client.delete(
        "/api/v1/users/nonexistent-uuid",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404