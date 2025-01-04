"""Test authentication routes."""

import json

import pytest
from fastapi.testclient import TestClient


from api.core.config import Settings


def test_github_login_success(client: TestClient, test_settings: Settings):
    """Test successful GitHub login route."""
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 200
    
    data = response.json()
    # Check response structure
    assert "auth_url" in data
    assert "state" in data
    
    # Verify auth_url format and parameters
    auth_url = data["auth_url"]
    assert auth_url.startswith("https://github.com/login/oauth/authorize")
    assert test_settings.DEV_GITHUB_CLIENT_ID in auth_url
    assert "scope=read:user" in auth_url
    assert data["state"] in auth_url
    
    # Verify state parameter
    assert len(data["state"]) > 20  # State should be a sufficiently long random string


def test_github_login_missing_client_id(client: TestClient, monkeypatch):
    """Test GitHub login route with missing client ID."""
    # Temporarily remove client ID from settings
    monkeypatch.setenv("DEV_GITHUB_CLIENT_ID", "")
    
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 500
    assert "GitHub client ID not configured" in response.json()["detail"]


def test_github_login_invalid_settings(client: TestClient, monkeypatch):
    """Test GitHub login route with invalid settings."""
    # Set invalid callback URL
    monkeypatch.setenv("DEV_GITHUB_CALLBACK_URL", "not-a-valid-url")
    
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 500
    assert "Invalid GitHub callback URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_github_callback_success(client: TestClient, monkeypatch):
    """Test successful GitHub callback."""
    # Mock the exchange_code_for_token method
    async def mock_exchange(*args, **kwargs):
        return {"access_token": "test-token", "token_type": "bearer"}
    
    monkeypatch.setattr(
        "api.auth.service.AuthService.exchange_code_for_token",
        mock_exchange
    )
    
    response = client.post(
        "/api/v1/auth/github",
        json={"code": "valid-code", "state": "valid-state"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_github_callback_invalid_state(client: TestClient):
    """Test GitHub callback with invalid state."""
    response = client.post(
        "/api/v1/auth/github",
        json={"code": "test-code", "state": "invalid-state"}
    )
    assert response.status_code == 400
    assert "Invalid OAuth state" in response.json()["detail"]


def test_github_callback_missing_code(client: TestClient):
    """Test GitHub callback with missing code."""
    response = client.post(
        "/api/v1/auth/github",
        json={"state": "valid-state"}
    )
    assert response.status_code == 422  # FastAPI validation error


def test_github_callback_invalid_code(client: TestClient):
    """Test GitHub callback with invalid code."""
    response = client.post(
        "/api/v1/auth/github",
        json={"code": "invalid-code", "state": "valid-state"}
    )
    assert response.status_code == 400
    assert "Failed to exchange code for token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_profile_success(client: TestClient, monkeypatch):
    """Test successful user profile retrieval."""
    # Mock GitHub API response
    class MockGitHubUser:
        id = 12345
        login = "test-user"
        avatar_url = "https://github.com/avatar.png"
        name = "Test User"
        email = "test@example.com"
    
    async def mock_get_github_user(*args, **kwargs):
        return MockGitHubUser()
    
    monkeypatch.setattr(
        "api.auth.service.AuthService._get_github_user",
        mock_get_github_user
    )
    
    response = client.get(
        "/api/v1/auth/user",
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "12345"
    assert data["username"] == "test-user"
    assert data["avatar_url"] == "https://github.com/avatar.png"
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"


def test_get_user_profile_unauthorized(client: TestClient):
    """Test get user profile without token."""
    response = client.get("/api/v1/auth/user")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_user_profile_invalid_token_format(client: TestClient):
    """Test get user profile with invalid token format."""
    response = client.get(
        "/api/v1/auth/user",
        headers={"Authorization": "InvalidFormat token-123"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_profile_github_error(client: TestClient, monkeypatch):
    """Test get user profile with GitHub API error."""
    async def mock_github_error(*args, **kwargs):
        raise ValueError("GitHub API error")
    
    monkeypatch.setattr(
        "api.auth.service.AuthService._get_github_user",
        mock_github_error
    )
    
    response = client.get(
        "/api/v1/auth/user",
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 500
    assert "Failed to fetch user profile" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_inventory_success(client: TestClient, monkeypatch):
    """Test successful inventory retrieval."""
    mock_inventory = {
        "gems": [
            {"id": "gem1", "type": "legendary", "rank": 5},
            {"id": "gem2", "type": "normal", "rank": 3}
        ]
    }
    
    async def mock_get_gist(*args, **kwargs):
        return {"files": {"inventory.json": {"content": json.dumps(mock_inventory)}}}
    
    monkeypatch.setattr(
        "api.auth.service.AuthService._get_gist",
        mock_get_gist
    )
    
    response = client.get(
        "/api/v1/auth/inventory",
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "gems" in data
    assert len(data["gems"]) == 2
    assert data["gems"][0]["id"] == "gem1"
    assert data["gems"][1]["rank"] == 3


def test_get_inventory_unauthorized(client: TestClient):
    """Test inventory retrieval without token."""
    response = client.get("/api/v1/auth/inventory")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_inventory_invalid_token(client: TestClient):
    """Test inventory retrieval with invalid token format."""
    response = client.get(
        "/api/v1/auth/inventory",
        headers={"Authorization": "InvalidFormat token-123"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_inventory_empty(client: TestClient, monkeypatch):
    """Test inventory retrieval with no existing inventory."""
    async def mock_get_empty_gist(*args, **kwargs):
        return {"files": {}}
    
    monkeypatch.setattr(
        "api.auth.service.AuthService._get_gist",
        mock_get_empty_gist
    )
    
    response = client.get(
        "/api/v1/auth/inventory",
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "gems" in data
    assert len(data["gems"]) == 0


@pytest.mark.asyncio
async def test_get_inventory_github_error(client: TestClient, monkeypatch):
    """Test inventory retrieval with GitHub API error."""
    async def mock_gist_error(*args, **kwargs):
        raise ValueError("GitHub API error")
    
    monkeypatch.setattr(
        "api.auth.service.AuthService._get_gist",
        mock_gist_error
    )
    
    response = client.get(
        "/api/v1/auth/inventory",
        headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 500
    assert "Failed to fetch inventory" in response.json()["detail"]
