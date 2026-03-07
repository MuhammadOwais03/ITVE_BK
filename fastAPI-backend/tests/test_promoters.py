"""Tests for /api/v1/promoters endpoints."""
from conftest import fake_promoters, FAKE_OBJ_ID


VALID_PROMOTER = {
    "email": "promoter@example.com",
    "password": "PromoPass1!",
    "phone": "+92 3005556677",
    "name": "Test Promoter",
}


def test_promoter_signup_success(client):
    resp = client.post("/api/v1/promoters/signup", json=VALID_PROMOTER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_type"] == "promoter"
    assert data["message"] == "Promoter registered successfully!"


def test_promoter_signup_duplicate_email(client):
    fake_promoters.find_one.side_effect = [
        {"_id": FAKE_OBJ_ID, "email": "promoter@example.com"},
    ]
    resp = client.post("/api/v1/promoters/signup", json=VALID_PROMOTER)
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_promoter_signup_duplicate_phone(client):
    fake_promoters.find_one.side_effect = [
        None,
        {"_id": FAKE_OBJ_ID, "phone": "+92 3005556677"},
    ]
    resp = client.post("/api/v1/promoters/signup", json=VALID_PROMOTER)
    assert resp.status_code == 400
    assert "Phone number already registered" in resp.json()["detail"]


def test_promoter_signup_invalid_phone(client):
    bad = {**VALID_PROMOTER, "phone": "not-a-phone"}
    resp = client.post("/api/v1/promoters/signup", json=bad)
    assert resp.status_code == 422


def test_promoter_signup_short_password(client):
    bad = {**VALID_PROMOTER, "password": "short"}
    resp = client.post("/api/v1/promoters/signup", json=bad)
    assert resp.status_code == 422


def test_promoter_signup_missing_name(client):
    bad = {k: v for k, v in VALID_PROMOTER.items() if k != "name"}
    resp = client.post("/api/v1/promoters/signup", json=bad)
    assert resp.status_code == 422
