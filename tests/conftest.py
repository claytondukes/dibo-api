"""Shared test fixtures and configuration."""

import pytest
from typing import Generator
import responses
from fastapi.testclient import TestClient

from api.main import app
from api.core.config import Settings, get_settings
from api.auth.service import AuthService, get_auth_service
from api.models.game_data.manager import GameDataManager
from api.builds.service import BuildService
from api.builds.routes import get_service

def get_test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        TESTING=True,
        ENVIRONMENT="test",
        LOG_LEVEL="DEBUG",
        DEBUG=True
    )

def get_test_auth_service() -> AuthService:
    """Get test auth service."""
    return AuthService(get_test_settings())

def get_test_data_manager() -> GameDataManager:
    """Get test data manager."""
    return GameDataManager(settings=get_test_settings())

async def get_test_build_service() -> BuildService:
    """Get test build service."""
    return await BuildService.create()

@pytest.fixture
def client() -> Generator:
    """FastAPI test client fixture."""
    # Create test instances
    settings = get_test_settings()
    data_manager = get_test_data_manager()
    
    # Override dependencies
    app.dependency_overrides[get_settings] = get_test_settings
    app.dependency_overrides[get_auth_service] = get_test_auth_service
    app.dependency_overrides[get_service] = get_test_build_service
    
    # Set app state
    app.state.data_manager = data_manager
    
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
