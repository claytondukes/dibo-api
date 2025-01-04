"""Test authentication flow."""

import os
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_github_login():
    """Test GitHub login endpoint."""
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert "github.com/login/oauth/authorize" in data["auth_url"]

def test_github_callback_invalid_state():
    """Test GitHub callback with invalid state."""
    response = client.post(
        "/api/v1/auth/github",
        json={"code": "test_code", "state": "invalid_state"}
    )
    assert response.status_code == 400
    assert "Invalid or expired state" in response.json()["detail"]

def test_user_profile_no_auth():
    """Test user profile endpoint without authentication."""
    response = client.get("/api/v1/auth/user")
    assert response.status_code == 401

def test_rate_limiting():
    """Test rate limiting."""
    # Test anonymous rate limit
    for _ in range(int(os.getenv("RATE_LIMIT_ANONYMOUS", "60"))):
        response = client.get("/api/v1/auth/github/login")
        assert response.status_code == 200
        
    # Next request should be rate limited
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
