"""
Shared fixtures for the entire test suite.
Patches Motor (async MongoDB) collections so **no real database** is required.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import pytest
from bson import ObjectId

# ---------------------------------------------------------------------------
# Make sure both the project root AND app/ are importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

# ---------------------------------------------------------------------------
# Fake Mongo helpers
# ---------------------------------------------------------------------------

FAKE_OBJ_ID = ObjectId()
FAKE_OBJ_ID_STR = str(FAKE_OBJ_ID)


class FakeInsertResult:
    """Mimics the object returned by ``collection.insert_one``."""
    def __init__(self, inserted_id=None):
        self.inserted_id = inserted_id or ObjectId()


class FakeUpdateResult:
    """Mimics the object returned by ``collection.update_one``."""
    def __init__(self, matched=1, modified=1):
        self.matched_count = matched
        self.modified_count = modified


class FakeCollection:
    """
    Lightweight async-capable mock for a Motor collection.
    Every method below is an AsyncMock so it can be awaited.
    Call ``configure(...)`` in individual tests to set the return values.
    """

    def __init__(self):
        self.find_one = AsyncMock(return_value=None)
        self.insert_one = AsyncMock(return_value=FakeInsertResult(FAKE_OBJ_ID))
        self.update_one = AsyncMock(return_value=FakeUpdateResult())
        self.count_documents = AsyncMock(return_value=0)
        self._find_results = []
        self.find = MagicMock(side_effect=self._fake_find)

    def _fake_find(self, *args, **kwargs):
        mock = MagicMock()
        mock.to_list = AsyncMock(return_value=self._find_results)
        return mock

    def reset(self):
        """Reset all mocks to defaults between tests."""
        self.find_one.reset_mock(return_value=True, side_effect=True)
        self.find_one.return_value = None
        self.find_one.side_effect = None
        self.insert_one.reset_mock(return_value=True, side_effect=True)
        self.insert_one.return_value = FakeInsertResult(FAKE_OBJ_ID)
        self.insert_one.side_effect = None
        self.update_one.reset_mock(return_value=True, side_effect=True)
        self.update_one.return_value = FakeUpdateResult()
        self.update_one.side_effect = None
        self.count_documents.reset_mock(return_value=True, side_effect=True)
        self.count_documents.return_value = 0
        self.count_documents.side_effect = None
        self._find_results = []


# Global fake collections – shared between conftest and the app under test
fake_students = FakeCollection()
fake_admins = FakeCollection()
fake_schools = FakeCollection()
fake_promoters = FakeCollection()
fake_workers = FakeCollection()
fake_teachers = FakeCollection()

# Map of collection name → FakeCollection instance
_COLLECTIONS = {
    "Students": fake_students,
    "Admins": fake_admins,
    "Schools": fake_schools,
    "Promoters": fake_promoters,
    "workers": fake_workers,
    "Workers": fake_workers,   # upload_documents uses capitalised "Workers"
    "teachers": fake_teachers,
}


class FakeDatabase:
    """Behaves like ``motor_client[db_name]``."""
    def __getitem__(self, name):
        if name not in _COLLECTIONS:
            _COLLECTIONS[name] = FakeCollection()
        return _COLLECTIONS[name]


# ---------------------------------------------------------------------------
# Patch ``get_database`` *before* importing the app so every module that calls
# ``get_database()`` at import time gets the fake.
# ---------------------------------------------------------------------------
_db_patch = patch("core.database.get_database", return_value=FakeDatabase())
_db_patch.start()

# Now import the app
from app.main import app  # noqa: E402
from core.security import create_access_token  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_collections():
    """Reset every fake collection before each test."""
    for col in _COLLECTIONS.values():
        col.reset()


@pytest.fixture()
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Auth helper tokens
# ---------------------------------------------------------------------------

def _make_token(user_type: str, sub: str | None = None, **extra):
    payload = {"sub": sub or FAKE_OBJ_ID_STR, "user_type": user_type, "email": "test@test.com"}
    payload.update(extra)
    return create_access_token(payload)


@pytest.fixture()
def admin_token():
    return _make_token("admin")


@pytest.fixture()
def student_token():
    return _make_token("Student")


@pytest.fixture()
def worker_token():
    return _make_token("worker")


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
