"""Test authentication routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from api.core.config import get_settings

settings = get_settings()


def test_github_login(client: TestClient):
    """Test GitHub login route."""
    response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert response.status_code == 200

    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert "Ov23liyqAQrjyTvPAQpI" in data["auth_url"]  # This is the actual client ID being used
    assert "http://localhost:8000/api/v1/auth/github" in data["auth_url"]


def test_github_callback_no_code(client: TestClient):
    """Test GitHub callback route with missing code."""
    response = client.get(
        f"{settings.API_V1_STR}/auth/github",
        params={"state": "test_state"}
    )
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["query", "code"]
    assert "required" in error["msg"].lower()


def test_github_callback_no_state(client: TestClient):
    """Test GitHub callback route with missing state."""
    response = client.get(
        f"{settings.API_V1_STR}/auth/github",
        params={"code": "test_code"}
    )
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["query", "state"]
    assert "required" in error["msg"].lower()


def test_github_callback_invalid_state(client: TestClient):
    """Test GitHub callback route with invalid state."""
    # First get a valid state
    login_response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert login_response.status_code == 200
    valid_state = login_response.json()["state"]

    # Then try with a different state
    response = client.get(
        f"{settings.API_V1_STR}/auth/github",
        params={
            "code": "test_code",
            "state": "invalid_state"
        }
    )
    assert response.status_code == 400
    assert "Invalid state parameter" in response.json()["detail"]


def test_github_callback_success(client: TestClient):
    """Test successful GitHub callback."""
    # First get a valid state
    login_response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert login_response.status_code == 200
    valid_state = login_response.json()["state"]

    # Mock the token exchange
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {
                "access_token": "gho_test",
                "token_type": "bearer",
                "scope": "read:user,gist"
            }
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/github",
            params={
                "code": "test_code",
                "state": valid_state
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


def test_get_inventory_unauthorized(client: TestClient):
    """Test getting inventory without authorization."""
    response = client.get(f"{settings.API_V1_STR}/auth/inventory")
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]
