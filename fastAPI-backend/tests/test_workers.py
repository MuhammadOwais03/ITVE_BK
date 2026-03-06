"""Tests for /api/v1/workers endpoints."""
from conftest import fake_workers, FAKE_OBJ_ID, auth_header


VALID_WORKER = {
    "name": "Test Worker",
    "cnic": "1234567890123",
    "job_type": "courses",
    "username": "test_worker",
}


# ── Auth required ─────────────────────────────────────────────────────────────

def test_add_worker_no_auth(client):
    resp = client.post("/api/v1/workers/add_worker", json=VALID_WORKER)
    assert resp.status_code == 401


# ── Admin only ────────────────────────────────────────────────────────────────

def test_add_worker_non_admin_forbidden(client, student_token):
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(student_token),
        json=VALID_WORKER,
    )
    assert resp.status_code == 403
    assert "Only admins" in resp.json()["detail"]


# ── Success ───────────────────────────────────────────────────────────────────

def test_add_worker_success(client, admin_token):
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=VALID_WORKER,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Worker added successfully!"
    assert data["username"] == "test_worker"
    assert data["job_type"] == "courses"


# ── Duplicate username ────────────────────────────────────────────────────────

def test_add_worker_duplicate_username(client, admin_token):
    fake_workers.find_one.side_effect = [
        {"_id": FAKE_OBJ_ID, "username": "test_worker"},  # username exists
    ]
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=VALID_WORKER,
    )
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


# ── Duplicate CNIC ────────────────────────────────────────────────────────────

def test_add_worker_duplicate_cnic(client, admin_token):
    fake_workers.find_one.side_effect = [
        None,  # username ok
        {"_id": FAKE_OBJ_ID, "cnic": "1234567890123"},  # cnic exists
    ]
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=VALID_WORKER,
    )
    assert resp.status_code == 400
    assert "CNIC already registered" in resp.json()["detail"]


# ── Validation errors ─────────────────────────────────────────────────────────

def test_add_worker_short_cnic(client, admin_token):
    bad = {**VALID_WORKER, "cnic": "12345"}
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422


def test_add_worker_invalid_job_type(client, admin_token):
    bad = {**VALID_WORKER, "job_type": "invalid"}
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422


def test_add_worker_non_digit_cnic(client, admin_token):
    bad = {**VALID_WORKER, "cnic": "123456789012a"}
    resp = client.post(
        "/api/v1/workers/add_worker",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422
