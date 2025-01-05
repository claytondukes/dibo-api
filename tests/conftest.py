"""Test configuration."""

import pytest
from fastapi.testclient import TestClient

from api.core.config import Settings, get_settings
from api.main import app


def get_settings_override() -> Settings:
    """Override settings for testing."""
    return Settings(
        PROJECT_NAME="Test API",
        VERSION="0.1.0",
        API_V1_STR="/api/v1",
        PROJECT_ROOT="/Users/cdukes/sourcecode/dibo-api",
        TESTING=True,
        ACTIVE_GITHUB_CLIENT_ID="test_client_id",
        ACTIVE_GITHUB_CLIENT_SECRET="test_client_secret",
        ACTIVE_GITHUB_CALLBACK_URL="http://localhost:8000/api/v1/auth/github/callback"
    )


@pytest.fixture
def test_settings() -> Settings:
    """Test settings fixture."""
    return get_settings_override()


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Test client fixture."""
    app.dependency_overrides[get_settings] = get_settings_override
    return TestClient(app)


@pytest.fixture
def mock_token() -> str:
    """Mock token fixture."""
    return "mock.test.token"


@pytest.fixture
def mock_access_token() -> str:
    """Mock GitHub access token."""
    return "gho_mock_token"


@pytest.fixture
def mock_github_token_response() -> dict:
    """Mock GitHub token response."""
    return {
        "access_token": "gho_mock_token",
        "scope": "read:user,gist",
        "token_type": "bearer"
    }


@pytest.fixture
def mock_github_user_response() -> dict:
    """Mock GitHub user response."""
    return {
        "login": "test_user",
        "id": 12345,
        "email": "test@example.com",
        "avatar_url": "https://github.com/test_user.png",
        "name": "Test User"
    }


@pytest.fixture
def mock_github_gists_response() -> list:
    """Mock GitHub gists response."""
    return [{
        "id": "gist123",
        "html_url": "https://gist.github.com/test123",
        "description": "DIBO Inventory",
        "files": {
            "builds.json": {
                "filename": "builds.json",
                "content": '{"version":"1.0","builds":[]}'
            },
            "profile.json": {
                "filename": "profile.json",
                "content": '{"version":"1.0","name":null}'
            },
            "gems.json": {
                "filename": "gems.json",
                "content": '{"version":"1.0","gems":[]}'
            },
            "sets.json": {
                "filename": "sets.json",
                "content": '{"version":"1.0","sets":[]}'
            }
        }
    }]


@pytest.fixture
def mock_gist_create_response() -> dict:
    """Mock gist creation response."""
    return {
        "id": "test123",
        "html_url": "https://gist.github.com/test123",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": true}'
            }
        }
    }


@pytest.fixture
def mock_gist_update_response() -> dict:
    """Mock gist update response."""
    return {
        "id": "test123",
        "html_url": "https://gist.github.com/test123",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": false, "updated": true}'
            }
        }
    }
