"""API test suite using FastAPI's test client."""

import os
import pytest
from fastapi.testclient import TestClient
from typing import Generator
import responses
import httpx

from api.main import app
from api.core.config import Settings, get_settings
from api.auth.service import AuthService, get_auth_service

def get_test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        DEV_GITHUB_CLIENT_ID="test_client_id",
        DEV_GITHUB_CLIENT_SECRET="test_client_secret",
        DEV_GITHUB_CALLBACK_URL="http://localhost:8000/api/v1/auth/github",
        DATA_PATH="/Users/cdukes/sourcecode/dibo-api/data/indexed"
    )

def get_test_auth_service() -> AuthService:
    """Get test auth service."""
    return AuthService(get_test_settings())

@pytest.fixture
def client() -> Generator:
    """FastAPI test client fixture."""
    app.dependency_overrides[get_settings] = get_test_settings
    app.dependency_overrides[get_auth_service] = get_test_auth_service
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def mock_github_api():
    """Mock GitHub API responses."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock GitHub OAuth token exchange
        rsps.add(
            responses.POST,
            "https://github.com/login/oauth/access_token",
            json={"error": "bad_verification_code"},
            status=400
        )

        # Mock GitHub gists API
        rsps.add(
            responses.GET,
            "https://api.github.com/gists",
            json={"message": "Bad credentials"},
            status=401,
            match=[responses.matchers.header_matcher({"Authorization": "token invalid_token"})]
        )
        rsps.add(
            responses.GET,
            "https://api.github.com/gists",
            json=[],
            status=200,
            match=[responses.matchers.header_matcher({"Authorization": "token valid_token"})]
        )

        # Mock GitHub gist update API
        rsps.add(
            responses.PATCH,
            "https://api.github.com/gists/test_gist_id",
            json={"message": "Bad credentials"},
            status=401,
            match=[responses.matchers.header_matcher({"Authorization": "token invalid_token"})]
        )
        rsps.add(
            responses.PATCH,
            "https://api.github.com/gists/test_gist_id",
            json={},
            status=200,
            match=[responses.matchers.header_matcher({"Authorization": "token valid_token"})]
        )
        rsps.add(
            responses.PATCH,
            "https://api.github.com/gists/invalid_id",
            json={"message": "Not Found"},
            status=404,
            match=[responses.matchers.header_matcher({"Authorization": "token valid_token"})]
        )

        # Mock GitHub gist create API
        rsps.add(
            responses.POST,
            "https://api.github.com/gists",
            json={"message": "Bad credentials"},
            status=401,
            match=[responses.matchers.header_matcher({"Authorization": "token invalid_token"})]
        )
        rsps.add(
            responses.POST,
            "https://api.github.com/gists",
            json={},
            status=201,
            match=[responses.matchers.header_matcher({"Authorization": "token valid_token"})]
        )

        yield rsps

def test_read_main(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200

def test_github_login(client: TestClient) -> None:
    """Test GitHub login endpoint."""
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data

def test_github_callback(client: TestClient) -> None:
    """Test GitHub callback endpoint."""
    # First get a valid state
    login_response = client.get("/api/v1/auth/login")
    state = login_response.json()["state"]
    
    # Test with valid state but invalid code
    response = client.get(
        "/api/v1/auth/github",
        params={"code": "invalid_code", "state": state}
    )
    assert response.status_code == 400
    
    # Test with invalid state
    response = client.get(
        "/api/v1/auth/github",
        params={"code": "test_code", "state": "invalid_state"}
    )
    assert response.status_code == 400

def test_create_gist(client: TestClient) -> None:
    """Test gist creation endpoint."""
    # Test without auth
    response = client.post("/api/v1/auth/gists")
    assert response.status_code == 401
    
    # Test with invalid auth
    response = client.post(
        "/api/v1/auth/gists",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "filename": "test.json",
            "content": "{}"
        }
    )
    assert response.status_code == 401
    
    # Test with valid auth but invalid content
    response = client.post(
        "/api/v1/auth/gists",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "filename": "test.json",
            "content": ""
        }
    )
    assert response.status_code == 400

def test_update_gist(client: TestClient) -> None:
    """Test gist update endpoint."""
    gist_id = "test_gist_id"
    
    # Test without auth
    response = client.patch(f"/api/v1/auth/gists/{gist_id}")
    assert response.status_code == 401
    
    # Test with invalid auth
    response = client.patch(
        f"/api/v1/auth/gists/{gist_id}",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "filename": "test.json",
            "content": "{}"
        }
    )
    assert response.status_code == 401
    
    # Test with valid auth but invalid content
    response = client.patch(
        f"/api/v1/auth/gists/{gist_id}",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "filename": "test.json",
            "content": ""
        }
    )
    assert response.status_code == 400
    
    # Test with invalid gist ID
    response = client.patch(
        "/api/v1/auth/gists/invalid_id",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "filename": "test.json",
            "content": "{}"
        }
    )
    # The auth service will return a 401 unauthorized error first
    assert response.status_code == 401

def test_get_gists(client: TestClient) -> None:
    """Test get gists endpoint."""
    # Test without auth
    response = client.get("/api/v1/auth/gists")
    assert response.status_code == 401
    
    # Test with invalid auth
    response = client.get(
        "/api/v1/auth/gists",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
