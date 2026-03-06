"""Tests for /api/v1/students endpoints."""
import io
import pytest
from unittest.mock import AsyncMock, patch
from conftest import (
    fake_students, FAKE_OBJ_ID, FAKE_OBJ_ID_STR, auth_header,
)
from core.security import hash_password


# ═══════════════════════════════════════════════════════════════════════
# SIGNUP
# ═══════════════════════════════════════════════════════════════════════

VALID_STUDENT = {
    "name": "Test Student",
    "gender": "male",
    "date_of_birth": "2005-01-15",
    "username": "test_student",
    "phone": "+92 3001234567",
    "email": "student@example.com",
    "password": "SecurePass1!",
}


def test_student_signup_success(client):
    resp = client.post("/api/v1/students/signup", json=VALID_STUDENT)
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Student registered successfully!"
    assert data["user_type"] == "Student"
    assert data["email"] == "student@example.com"


def test_student_signup_duplicate_username(client):
    fake_students.find_one.side_effect = [
        {"_id": FAKE_OBJ_ID, "username": "test_student"},  # username exists
    ]
    resp = client.post("/api/v1/students/signup", json=VALID_STUDENT)
    assert resp.status_code == 400
    assert "Username already taken" in resp.json()["detail"]


def test_student_signup_duplicate_email(client):
    fake_students.find_one.side_effect = [
        None,  # username ok
        {"_id": FAKE_OBJ_ID, "email": "student@example.com"},  # email exists
    ]
    resp = client.post("/api/v1/students/signup", json=VALID_STUDENT)
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_student_signup_duplicate_phone(client):
    fake_students.find_one.side_effect = [
        None,  # username ok
        None,  # email ok
        {"_id": FAKE_OBJ_ID, "phone": "+92 3001234567"},  # phone exists
    ]
    resp = client.post("/api/v1/students/signup", json=VALID_STUDENT)
    assert resp.status_code == 400
    assert "Phone number already registered" in resp.json()["detail"]


def test_student_signup_invalid_phone(client):
    bad = {**VALID_STUDENT, "phone": "1234567890"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


def test_student_signup_weak_password(client):
    bad = {**VALID_STUDENT, "password": "nodigits!"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


def test_student_signup_invalid_dob(client):
    bad = {**VALID_STUDENT, "date_of_birth": "not-a-date"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


def test_student_signup_too_young(client):
    bad = {**VALID_STUDENT, "date_of_birth": "2024-01-01"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


def test_student_signup_invalid_email(client):
    bad = {**VALID_STUDENT, "email": "not-an-email"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


def test_student_signup_invalid_gender(client):
    bad = {**VALID_STUDENT, "gender": "other"}
    resp = client.post("/api/v1/students/signup", json=bad)
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# UPLOAD PROFILE IMAGE
# ═══════════════════════════════════════════════════════════════════════

def test_upload_profile_no_auth(client):
    resp = client.post("/api/v1/students/upload_profile")
    assert resp.status_code == 401  # HTTPBearer returns 401


@patch("services.student_service.aiofiles", create=True)
def test_upload_profile_success(mock_aiofiles, client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "profile_image": None
    }

    # Mock aiofiles.open context manager
    mock_file = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_file)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    mock_aiofiles.open.return_value = mock_cm

    file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # fake JPEG bytes
    resp = client.post(
        "/api/v1/students/upload_profile",
        headers=auth_header(student_token),
        files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Image uploaded successfully"
    assert "filename" in data


def test_upload_profile_invalid_extension(client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "profile_image": None
    }
    resp = client.post(
        "/api/v1/students/upload_profile",
        headers=auth_header(student_token),
        files={"file": ("test.gif", io.BytesIO(b"GIF89a"), "image/gif")},
    )
    assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
# UPDATE STUDENT PROFILE
# ═══════════════════════════════════════════════════════════════════════

def test_update_student_no_auth(client):
    resp = client.put("/api/v1/students/update", json={"name": "New"})
    assert resp.status_code == 401


def test_update_student_no_changes(client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "username": "old", "password": hash_password("OldPass1!")
    }
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "No changes made"


def test_update_student_name(client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "username": "old", "password": hash_password("OldPass1!")
    }
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={"name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert "name" in resp.json()["updated_fields"]


def test_update_student_password_success(client, student_token):
    hashed = hash_password("OldPass1!")
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "username": "user1", "password": hashed
    }
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={
            "old_password": "OldPass1!",
            "new_password": "NewPass2@",
            "confirm_new_password": "NewPass2@",
        },
    )
    assert resp.status_code == 200
    assert "password" in resp.json()["updated_fields"]


def test_update_student_password_incomplete(client, student_token):
    """Providing only old_password without new passwords should fail validation."""
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={"old_password": "SomePass1!"},
    )
    assert resp.status_code == 422


def test_update_student_password_mismatch(client, student_token):
    """new_password != confirm_new_password should fail validation."""
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={
            "old_password": "OldPass1!",
            "new_password": "NewPass2@",
            "confirm_new_password": "Different3#",
        },
    )
    assert resp.status_code == 422


def test_update_student_wrong_old_password(client, student_token):
    hashed = hash_password("RealOldPass1!")
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "username": "user1", "password": hashed
    }
    resp = client.put(
        "/api/v1/students/update",
        headers=auth_header(student_token),
        json={
            "old_password": "WrongOldPass1!",
            "new_password": "NewSecure2@",
            "confirm_new_password": "NewSecure2@",
        },
    )
    assert resp.status_code == 400
    assert "Old password" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════════════
# GET PROFILE
# ═══════════════════════════════════════════════════════════════════════

def test_get_profile_no_auth(client):
    resp = client.get("/api/v1/students/profile")
    assert resp.status_code == 401


def test_get_profile_success(client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID,
        "username": "stu1",
        "name": "Student One",
        "bio": None,
        "location": None,
        "gender": "male",
        "date_of_birth": "2005-01-01",
        "school": "Test School",
        "profile_image": None,
        "work": None,
        "edu": None,
        "interests": ["coding"],
        "skills": ["python"],
        "programming_languages": ["python"],
        "languages": ["english"],
    }
    resp = client.get("/api/v1/students/profile", headers=auth_header(student_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "stu1"
    assert data["name"] == "Student One"


def test_get_profile_not_found(client, student_token):
    fake_students.find_one.return_value = None
    resp = client.get("/api/v1/students/profile", headers=auth_header(student_token))
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
# STATUS UPDATE
# ═══════════════════════════════════════════════════════════════════════

def test_status_update_no_auth(client):
    resp = client.patch("/api/v1/students/status", json={"status": "active"})
    assert resp.status_code == 401


def test_status_update_active(client, student_token):
    resp = client.patch(
        "/api/v1/students/status",
        headers=auth_header(student_token),
        json={"status": "active"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_active"] is True


def test_status_update_inactive(client, student_token):
    resp = client.patch(
        "/api/v1/students/status",
        headers=auth_header(student_token),
        json={"status": "inactive", "reason": "taking a break"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_status_update_deleted(client, student_token):
    resp = client.patch(
        "/api/v1/students/status",
        headers=auth_header(student_token),
        json={"status": "deleted", "reason": "no longer needed"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_active"] is False


def test_status_update_invalid(client, student_token):
    resp = client.patch(
        "/api/v1/students/status",
        headers=auth_header(student_token),
        json={"status": "banned"},
    )
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# REMOVE PROFILE IMAGE
# ═══════════════════════════════════════════════════════════════════════

def test_remove_profile_image_no_auth(client):
    resp = client.delete("/api/v1/students/remove_profile_image")
    assert resp.status_code == 401


def test_remove_profile_image_success(client, student_token):
    fake_students.find_one.return_value = {
        "_id": FAKE_OBJ_ID, "profile_image": None
    }
    resp = client.delete(
        "/api/v1/students/remove_profile_image",
        headers=auth_header(student_token),
    )
    assert resp.status_code == 200
    assert "removed" in resp.json()["message"].lower()
