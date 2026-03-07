"""Tests for /api/v1/teachers endpoints."""
from bson import ObjectId
from conftest import fake_teachers, fake_workers, FAKE_OBJ_ID, FAKE_OBJ_ID_STR, auth_header
from core.security import create_access_token


VALID_TEACHER = {
    "course": "english",
    "username": "teacher_user",
    "password": "TeachPass@1",
}


# ── Auth required ─────────────────────────────────────────────────────────────

def test_generate_teacher_no_auth(client):
    resp = client.post("/api/v1/teachers/generate_teacher_account", json=VALID_TEACHER)
    assert resp.status_code == 401


# ── Role check: student forbidden ─────────────────────────────────────────────

def test_generate_teacher_student_forbidden(client, student_token):
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(student_token),
        json=VALID_TEACHER,
    )
    assert resp.status_code == 403
    assert "Only admins and courses-workers" in resp.json()["detail"]


# ── Admin success ─────────────────────────────────────────────────────────────

def test_generate_teacher_admin_success(client, admin_token):
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(admin_token),
        json=VALID_TEACHER,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Teacher account created successfully!"
    assert data["username"] == "teacher_user"
    assert data["course"] == "english"


# ── Worker with courses job type → success ────────────────────────────────────

def test_generate_teacher_worker_courses_success(client):
    worker_id = ObjectId()
    token = create_access_token({
        "sub": str(worker_id),
        "user_type": "worker",
        "email": "worker@test.com",
    })
    fake_workers.find_one.return_value = {
        "_id": worker_id,
        "job_type": "courses",
        "username": "worker1",
    }
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(token),
        json=VALID_TEACHER,
    )
    assert resp.status_code == 201


# ── Worker with reports job type → 403 ────────────────────────────────────────

def test_generate_teacher_worker_reports_forbidden(client):
    worker_id = ObjectId()
    token = create_access_token({
        "sub": str(worker_id),
        "user_type": "worker",
        "email": "worker@test.com",
    })
    fake_workers.find_one.return_value = {
        "_id": worker_id,
        "job_type": "reports",
        "username": "worker1",
    }
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(token),
        json=VALID_TEACHER,
    )
    assert resp.status_code == 403
    assert "job type 'courses'" in resp.json()["detail"]


# ── Duplicate username ────────────────────────────────────────────────────────

def test_generate_teacher_duplicate_username(client, admin_token):
    fake_teachers.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "username": "teacher_user"
    }
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(admin_token),
        json=VALID_TEACHER,
    )
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


# ── Validation: invalid course ────────────────────────────────────────────────

def test_generate_teacher_invalid_course(client, admin_token):
    bad = {**VALID_TEACHER, "course": "physics"}
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422


# ── Validation: weak password (no uppercase) ──────────────────────────────────

def test_generate_teacher_weak_password(client, admin_token):
    bad = {**VALID_TEACHER, "password": "noupperletter1!"}
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422


# ── Validation: short password ────────────────────────────────────────────────

def test_generate_teacher_short_password(client, admin_token):
    bad = {**VALID_TEACHER, "password": "Sh1!"}
    resp = client.post(
        "/api/v1/teachers/generate_teacher_account",
        headers=auth_header(admin_token),
        json=bad,
    )
    assert resp.status_code == 422
