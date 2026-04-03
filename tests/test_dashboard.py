import pytest


def test_viewer_can_access_summary(client, viewer_token):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "net_balance" in data
    assert "financial_health" in data


def test_summary_values_are_correct(client, admin_token, sample_record):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    data = response.json()
    assert data["total_income"] >= 5000.00
    assert data["net_balance"] == round(data["total_income"] - data["total_expenses"], 2)


def test_viewer_can_access_categories(client, viewer_token, sample_record):
    response = client.get(
        "/api/v1/dashboard/categories",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 200
    assert "income_by_category" in response.json()
    assert "expense_by_category" in response.json()


def test_analyst_can_access_monthly_trends(client, analyst_token):
    response = client.get(
        "/api/v1/dashboard/trends/monthly?year=2026",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert len(data["monthly_trends"]) == 12


def test_viewer_cannot_access_monthly_trends(client, viewer_token):
    response = client.get(
        "/api/v1/dashboard/trends/monthly",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


def test_weekly_trends_valid_range(client, analyst_token):
    response = client.get(
        "/api/v1/dashboard/trends/weekly?date_from=2026-01-01&date_to=2026-03-01",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert "weekly_trends" in response.json()


def test_weekly_trends_range_exceeds_90_days(client, analyst_token):
    response = client.get(
        "/api/v1/dashboard/trends/weekly?date_from=2026-01-01&date_to=2026-12-31",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 400
    assert "90 days" in response.json()["detail"]


def test_recent_activity_accessible_by_viewer(client, viewer_token, sample_record):
    response = client.get(
        "/api/v1/dashboard/recent?limit=5",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 200
    assert "recent_activity" in response.json()
    assert len(response.json()["recent_activity"]) <= 5


def test_unauthenticated_cannot_access_dashboard(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 403