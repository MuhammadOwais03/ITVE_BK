"""Tests for /api/v1/admins endpoints."""
from conftest import fake_admins, FAKE_OBJ_ID


VALID_ADMIN = {
    "email": "admin@example.com",
    "password": "AdminPass1!",
    "phone": "+92 3009876543",
    "username": "admin_user",
    "admin_code": "",   # will be patched per-test
}


def test_admin_signup_invalid_code(client):
    payload = {**VALID_ADMIN, "admin_code": "wrong-code"}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 403
    assert "Invalid admin code" in resp.json()["detail"]


def test_admin_signup_success(client):
    # Use the default ADMIN_SECRET_CODE from settings (set to "" or read from env)
    from core.config import settings
    payload = {**VALID_ADMIN, "admin_code": settings.ADMIN_SECRET_CODE}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_type"] == "admin"
    assert data["message"] == "Admin registered successfully!"


def test_admin_signup_duplicate_email(client):
    from core.config import settings
    fake_admins.find_one.side_effect = [
        {"_id": FAKE_OBJ_ID, "email": "admin@example.com"},  # email exists
    ]
    payload = {**VALID_ADMIN, "admin_code": settings.ADMIN_SECRET_CODE}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_admin_signup_duplicate_phone(client):
    from core.config import settings
    fake_admins.find_one.side_effect = [
        None,  # email ok
        {"_id": FAKE_OBJ_ID, "phone": "+92 3009876543"},  # phone exists
    ]
    payload = {**VALID_ADMIN, "admin_code": settings.ADMIN_SECRET_CODE}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 400
    assert "Phone number already registered" in resp.json()["detail"]


def test_admin_signup_invalid_phone(client):
    from core.config import settings
    payload = {**VALID_ADMIN, "admin_code": settings.ADMIN_SECRET_CODE, "phone": "12345"}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 422


def test_admin_signup_short_password(client):
    from core.config import settings
    payload = {**VALID_ADMIN, "admin_code": settings.ADMIN_SECRET_CODE, "password": "short"}
    resp = client.post("/api/v1/admins/signup", json=payload)
    assert resp.status_code == 422
