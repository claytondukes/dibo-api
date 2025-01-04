"""Test authentication routes."""

import pytest
from fastapi.testclient import TestClient

from api.core.config import Settings


def test_github_login(client: TestClient, test_settings: Settings):
    """Test GitHub login route."""
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 200
    
    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert "Ov23liNuYPvWzwNkmC73" in data["auth_url"]


def test_github_callback_invalid_state(client: TestClient):
    """Test GitHub callback with invalid state."""
    response = client.post(
        "/api/v1/auth/github",
        json={"code": "test-code", "state": "invalid-state"}
    )
    assert response.status_code == 400
    assert "Invalid OAuth state" in response.json()["detail"]


def test_get_user_profile_unauthorized(client: TestClient):
    """Test get user profile without token."""
    response = client.get("/api/v1/auth/user")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
