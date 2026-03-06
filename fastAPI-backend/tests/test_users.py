"""Tests for /api/v1/users endpoints (count & list)."""
from bson import ObjectId
from conftest import fake_admins, fake_students, fake_schools, fake_promoters


def test_get_users_count(client):
    fake_admins.count_documents.return_value = 2
    fake_students.count_documents.return_value = 10
    fake_schools.count_documents.return_value = 3
    fake_promoters.count_documents.return_value = 5

    resp = client.get("/api/v1/users/count")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 20
    assert data["admins"] == 2
    assert data["students"] == 10
    assert data["schools_colleges"] == 3
    assert data["promoters"] == 5


def test_get_users_count_empty(client):
    resp = client.get("/api/v1/users/count")
    assert resp.status_code == 200
    assert resp.json()["total_users"] == 0


def test_get_all_users_list(client):
    fake_admins._find_results = [
        {"_id": ObjectId(), "email": "admin@test.com", "user_type": "admin"},
    ]
    fake_students._find_results = [
        {"_id": ObjectId(), "email": "stu@test.com", "user_type": "Student"},
    ]
    fake_schools._find_results = []
    fake_promoters._find_results = []

    resp = client.get("/api/v1/users/all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 2
    assert len(data["users"]) == 2


def test_get_all_users_empty(client):
    resp = client.get("/api/v1/users/all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 0
    assert data["users"] == []
