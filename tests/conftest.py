"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from api.core.config import Settings, get_settings
from api.main import app


def get_settings_override():
    """Override settings for testing."""
    return Settings(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        BACKEND_CORS_ORIGINS=["http://localhost:3000"]
    )


@pytest.fixture
def test_settings():
    """Test settings fixture."""
    return get_settings_override()


@pytest.fixture
def client():
    """Test client fixture."""
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
