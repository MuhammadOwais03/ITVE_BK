"""Tests for root and basic app functionality."""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

from conftest import auth_header  # noqa: E402


def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "docs" in data


def test_docs_redirect(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
