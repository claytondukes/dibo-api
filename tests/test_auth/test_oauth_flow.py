"""Test complete OAuth flow with mocked GitHub responses."""

import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
import httpx

from dibo_api.core.config import Settings


@pytest.fixture
def mock_github_user_response():
    """Mock GitHub user API response."""
    return {
        "id": 12345,
        "login": "test_user",
        "avatar_url": "https://github.com/test_user.png",
        "name": "Test User",
        "email": "test@example.com"
    }


@pytest.fixture
def mock_github_token_response():
    """Mock GitHub token API response."""
    return {
        "access_token": "gho_mock_token",
        "token_type": "bearer",
        "scope": "read:user,gist"
    }


def test_complete_oauth_flow(
    client: TestClient,
    test_settings: Settings,
    mock_github_token_response,
    mock_github_user_response
):
    """Test the complete OAuth flow with mocked responses."""
    # Step 1: Get the login URL and state
    login_response = client.get("/api/v1/auth/github/login")
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "state" in login_data
    state = login_data["state"]

    # Step 2: Mock the GitHub token exchange
    with patch(
        "httpx.AsyncClient.post",
        return_value=httpx.Response(
            200,
            json=mock_github_token_response
        )
    ):
        # Step 3: Mock the GitHub user info request
        with patch(
            "httpx.AsyncClient.get",
            return_value=httpx.Response(
                200,
                json=mock_github_user_response
            )
        ):
            # Simulate the callback from GitHub
            callback_response = client.post(
                "/api/v1/auth/github",
                json={"code": "test_code", "state": state}
            )
            assert callback_response.status_code == 200
            token_data = callback_response.json()
            
            # Verify response structure
            assert "access_token" in token_data
            assert "token_type" in token_data
            assert "scope" in token_data
            assert "user" in token_data
            
            # Verify user data
            user_data = token_data["user"]
            assert user_data["id"] == str(mock_github_user_response["id"])
            assert user_data["username"] == mock_github_user_response["login"]
            assert user_data["avatar_url"] == mock_github_user_response["avatar_url"]

            # Test accessing a protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            profile_response = client.get("/api/v1/auth/user", headers=headers)
            assert profile_response.status_code == 200
            assert profile_response.json()["username"] == mock_github_user_response["login"]


def test_github_token_exchange_failure(client: TestClient, test_settings: Settings):
    """Test handling of GitHub token exchange failure."""
    # Get valid state token first
    login_response = client.get("/api/v1/auth/github/login")
    state = login_response.json()["state"]

    # Mock a failed token exchange
    with patch(
        "httpx.AsyncClient.post",
        return_value=httpx.Response(400, text="Bad Request")
    ):
        response = client.post(
            "/api/v1/auth/github",
            json={"code": "invalid_code", "state": state}
        )
        assert response.status_code == 400
        assert "Failed to exchange code for token" in response.json()["detail"]


def test_github_user_info_failure(
    client: TestClient,
    test_settings: Settings,
    mock_github_token_response
):
    """Test handling of GitHub user info fetch failure."""
    # Get valid state token first
    login_response = client.get("/api/v1/auth/github/login")
    state = login_response.json()["state"]

    # Mock successful token exchange but failed user info
    with patch(
        "httpx.AsyncClient.post",
        return_value=httpx.Response(
            200,
            json=mock_github_token_response
        )
    ):
        with patch(
            "httpx.AsyncClient.get",
            return_value=httpx.Response(401, text="Unauthorized")
        ):
            response = client.post(
                "/api/v1/auth/github",
                json={"code": "test_code", "state": state}
            )
            assert response.status_code == 400
            assert "Failed to fetch user info" in response.json()["detail"]
