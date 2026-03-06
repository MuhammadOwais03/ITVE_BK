"""Tests for /api/v1/schools endpoints."""
from conftest import fake_schools, FAKE_OBJ_ID


VALID_SCHOOL = {
    "email": "school@example.com",
    "password": "SchoolPass1!",
    "phone": "+92 3001112233",
    "institute_name": "Test Academy",
    "address": "123 Education Street, Lahore",
}


def test_school_signup_success(client):
    resp = client.post("/api/v1/schools/signup", json=VALID_SCHOOL)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_type"] == "school/college"
    assert data["message"] == "School/College registered successfully!"


def test_school_signup_duplicate_email(client):
    fake_schools.find_one.side_effect = [
        {"_id": FAKE_OBJ_ID, "email": "school@example.com"},
    ]
    resp = client.post("/api/v1/schools/signup", json=VALID_SCHOOL)
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_school_signup_duplicate_phone(client):
    fake_schools.find_one.side_effect = [
        None,
        {"_id": FAKE_OBJ_ID, "phone": "+92 3001112233"},
    ]
    resp = client.post("/api/v1/schools/signup", json=VALID_SCHOOL)
    assert resp.status_code == 400
    assert "Phone number already registered" in resp.json()["detail"]


def test_school_signup_with_head_of_institute(client):
    payload = {**VALID_SCHOOL, "head_of_institute": "Dr. Principal"}
    resp = client.post("/api/v1/schools/signup", json=payload)
    assert resp.status_code == 201


def test_school_signup_invalid_phone(client):
    bad = {**VALID_SCHOOL, "phone": "0300-1234567"}
    resp = client.post("/api/v1/schools/signup", json=bad)
    assert resp.status_code == 422


def test_school_signup_short_address(client):
    bad = {**VALID_SCHOOL, "address": "hi"}
    resp = client.post("/api/v1/schools/signup", json=bad)
    assert resp.status_code == 422


def test_school_signup_missing_institute_name(client):
    bad = {k: v for k, v in VALID_SCHOOL.items() if k != "institute_name"}
    resp = client.post("/api/v1/schools/signup", json=bad)
    assert resp.status_code == 422
