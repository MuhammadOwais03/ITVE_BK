"""Tests for /api/v1/auth endpoints."""
import pytest
from conftest import (
    fake_students, fake_admins, fake_schools, fake_promoters,
    FAKE_OBJ_ID, auth_header,
)
from core.security import hash_password


# ── Login: missing fields → 422 ──────────────────────────────────────────────

def test_login_missing_password(client):
    resp = client.post("/api/v1/auth/login", json={"username_or_email": "user@example.com"})
    assert resp.status_code == 422


def test_login_missing_username(client):
    resp = client.post("/api/v1/auth/login", json={"password": "Pass1234!"})
    assert resp.status_code == 422


# ── Login: password too short → 422 ──────────────────────────────────────────

def test_login_short_password(client):
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "user@example.com",
        "password": "short"
    })
    assert resp.status_code == 422


# ── Login: user not found → 404 ──────────────────────────────────────────────

def test_login_user_not_found(client):
    # All find_one return None by default
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "nobody@example.com",
        "password": "LongEnough1!"
    })
    assert resp.status_code == 404


# ── Login: wrong password → 401 ──────────────────────────────────────────────

def test_login_wrong_password(client):
    fake_user = {
        "_id": FAKE_OBJ_ID,
        "email": "student@test.com",
        "username": "student1",
        "password": hash_password("CorrectPass1!"),
        "user_type": "Student",
        "is_active": True,
    }
    fake_students.find_one.return_value = fake_user

    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "student1",
        "password": "WrongPass1!"
    })
    assert resp.status_code == 401


# ── Login: successful student login → 200 ────────────────────────────────────

def test_login_success_student(client):
    hashed = hash_password("CorrectPass1!")
    fake_user = {
        "_id": FAKE_OBJ_ID,
        "email": "student@test.com",
        "username": "student1",
        "password": hashed,
        "user_type": "Student",
        "is_active": True,
    }
    fake_students.find_one.return_value = fake_user

    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "student1",
        "password": "CorrectPass1!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Login successful!"
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user_type"] == "Student"


# ── Login: deleted account → 403 ─────────────────────────────────────────────

def test_login_deleted_account(client):
    hashed = hash_password("CorrectPass1!")
    fake_user = {
        "_id": FAKE_OBJ_ID,
        "email": "del@test.com",
        "username": "deleted_user",
        "password": hashed,
        "user_type": "Student",
        "is_deleted": True,
        "is_active": False,
    }
    fake_students.find_one.return_value = fake_user

    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "deleted_user",
        "password": "CorrectPass1!"
    })
    assert resp.status_code == 403


# ── Login: inactive account auto-reactivated → 200 ──────────────────────────

def test_login_reactivates_inactive(client):
    hashed = hash_password("CorrectPass1!")
    fake_user = {
        "_id": FAKE_OBJ_ID,
        "email": "inactive@test.com",
        "username": "inactive_user",
        "password": hashed,
        "user_type": "Student",
        "is_active": False,
        "is_deleted": False,
    }
    fake_students.find_one.return_value = fake_user

    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "inactive_user",
        "password": "CorrectPass1!"
    })
    assert resp.status_code == 200
    # Should have called update_one to reactivate
    fake_students.update_one.assert_awaited()
