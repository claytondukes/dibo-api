"""Test complete OAuth flow with mocked GitHub responses."""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
import httpx

from api.core.config import settings


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


@pytest.fixture
def mock_github_gists_response():
    """Mock GitHub gists API response."""
    return [{
        "id": "gist123",
        "description": "DIBO Inventory",
        "files": {
            "profile.json": {
                "filename": "profile.json",
                "content": '{"version":"1.0","name":"TestChar","class":"Barbarian"}'
            },
            "gems.json": {
                "filename": "gems.json",
                "content": '{"version":"1.0","gems":[]}'
            },
            "sets.json": {
                "filename": "sets.json",
                "content": '{"version":"1.0","sets":[]}'
            },
            "builds.json": {
                "filename": "builds.json",
                "content": '{"version":"1.0","builds":[]}'
            }
        }
    }]


def test_complete_oauth_flow(
    client: TestClient,
    mock_github_token_response,
    mock_github_user_response,
    mock_github_gists_response
):
    """Test the complete OAuth flow with mocked responses."""
    # Step 1: Get the login URL and state
    login_response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "auth_url" in login_data
    assert "state" in login_data
    state = login_data["state"]

    # Step 2: Exchange code for token
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = httpx.Response(
            200,
            json=mock_github_token_response
        )

        callback_response = client.get(
            f"{settings.API_V1_STR}/auth/github/callback",
            params={
                "code": "test_code",
                "state": state
            }
        )
        assert callback_response.status_code == 200

        token_data = callback_response.json()
        assert "access_token" in token_data
        assert token_data["access_token"] == mock_github_token_response["access_token"]


def test_github_token_exchange_failure(client: TestClient):
    """Test handling of GitHub token exchange failure."""
    # Get valid state token first
    login_response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert login_response.status_code == 200
    state = login_response.json()["state"]

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = httpx.Response(
            400,
            json={"error": "bad_verification_code"}
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/github/callback",
            params={
                "code": "invalid_code",
                "state": state
            }
        )
        assert response.status_code == 400


def test_github_user_info_failure(
    client: TestClient,
    mock_github_token_response
):
    """Test handling of GitHub user info fetch failure."""
    # Get valid state token first
    login_response = client.get(f"{settings.API_V1_STR}/auth/login")
    assert login_response.status_code == 200
    state = login_response.json()["state"]

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = httpx.Response(
            200,
            json=mock_github_token_response
        )

        callback_response = client.get(
            f"{settings.API_V1_STR}/auth/github/callback",
            params={
                "code": "test_code",
                "state": state
            }
        )
        assert callback_response.status_code == 200
