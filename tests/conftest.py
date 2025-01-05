"""Test configuration and fixtures."""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from api.core.config import Settings, get_settings
from api.main import app

# Set test environment variables
os.environ.update({
    'PROJECT_ROOT': str(Path(__file__).parent.parent),
    'DATA_DIR': str(Path(__file__).parent.parent / 'data' / 'indexed'),
    'TESTING': 'true',
    'ENVIRONMENT': 'development',
    'LOG_LEVEL': 'INFO',
    'RATE_LIMIT_AUTHENTICATED': '1000',
    'RATE_LIMIT_ANONYMOUS': '60',
    'DEV_GITHUB_CALLBACK_URL': 'http://localhost:8000/api/v1/auth/github'
})


@pytest.fixture
def test_settings():
    """Override settings for testing.
    
    Returns:
        Settings: Test settings with environment variables applied
    """
    return Settings()


@pytest.fixture
def client(test_settings):
    """Test client fixture."""
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment."""
    yield
