"""Shared test fixtures and configuration."""

import pytest
from typing import Generator
import responses
from fastapi.testclient import TestClient

from api.main import app
from api.core.config import Settings, get_settings
from api.auth.service import AuthService, get_auth_service

def get_test_settings() -> Settings:
    """Get test settings."""
    # Settings will automatically load from .env
    return Settings(TESTING=True)

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

        yield rsps
