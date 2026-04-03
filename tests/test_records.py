import pytest
from datetime import date


CREATE_PAYLOAD = {
    "amount": 3000.00,
    "type": "income",
    "category": "salary",
    "record_date": "2026-03-01",
    "notes": "March salary",
}


def test_admin_can_create_record(client, admin_token):
    response = client.post(
        "/api/v1/records/",
        json=CREATE_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 3000.00
    assert response.json()["type"] == "income"


def test_analyst_cannot_create_record(client, analyst_token):
    response = client.post(
        "/api/v1/records/",
        json=CREATE_PAYLOAD,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403


def test_viewer_cannot_create_record(client, viewer_token):
    response = client.post(
        "/api/v1/records/",
        json=CREATE_PAYLOAD,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


def test_mismatched_category_type_rejected(client, admin_token):
    response = client.post(
        "/api/v1/records/",
        json={
            "amount": 100.00,
            "type": "income",
            "category": "food",       # food is an expense category
            "record_date": "2026-03-01",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


def test_negative_amount_rejected(client, admin_token):
    response = client.post(
        "/api/v1/records/",
        json={
            "amount": -500.00,
            "type": "expense",
            "category": "food",
            "record_date": "2026-03-01",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


def test_analyst_can_list_records(client, analyst_token, sample_record):
    response = client.get(
        "/api/v1/records/",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_viewer_cannot_list_records(client, viewer_token):
    response = client.get(
        "/api/v1/records/",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


def test_filter_by_type(client, analyst_token, sample_record):
    response = client.get(
        "/api/v1/records/?type=income",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    for record in response.json()["results"]:
        assert record["type"] == "income"


def test_filter_by_invalid_date_range(client, analyst_token):
    response = client.get(
        "/api/v1/records/?date_from=2026-03-31&date_to=2026-03-01",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 400


def test_admin_can_soft_delete_record(client, admin_token, sample_record):
    delete = client.delete(
        f"/api/v1/records/{sample_record.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete.status_code == 200

    fetch = client.get(
        f"/api/v1/records/{sample_record.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert fetch.status_code == 404

def test_soft_deleted_record_not_accessible(client, admin_token, analyst_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    create_resp = client.post(
        "/api/v1/records/",
        json={
            "title": "Temp Record",
            "amount": 100.00,
            "type": "income",
            "category": "other_income",
            "record_date": "2025-06-01",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    record_id = create_resp.json()["id"]

    client.delete(f"/api/v1/records/{record_id}", headers=headers)

    get_resp = client.get(f"/api/v1/records/{record_id}", headers=analyst_headers)
    assert get_resp.status_code == 404


def test_analyst_can_get_record_by_id(client, admin_token, analyst_token):
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    create_resp = client.post(
        "/api/v1/records/",
        json={
            "title": "Analyst Read Test",
            "amount": 200.00,
            "type": "income",
            "category": "salary",
            "record_date": "2025-06-15",
        },
        headers=admin_headers,
    )
    assert create_resp.status_code == 201
    record_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/records/{record_id}", headers=analyst_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == record_id


def test_admin_can_update_record_amount(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    create_resp = client.post(
        "/api/v1/records/",
        json={
            "title": "Update Test Record",
            "amount": 500.00,
            "type": "expense",
            "category": "utilities",
            "record_date": "2025-07-01",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    record_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/v1/records/{record_id}",
        json={"amount": 750.00},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["amount"] == 750.00