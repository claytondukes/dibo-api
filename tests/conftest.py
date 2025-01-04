"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from api.core.config import Settings, get_settings
from api.main import app


def get_settings_override():
    """Override settings for testing.
    
    Returns:
        Settings: Test settings with:
            - PROJECT_ROOT: Set to the root of the test project
            - TESTING: Set to True to indicate test environment
            
    This provides the minimum settings needed for testing the build service.
    Database and API settings are not needed since we're using mock data.
    """
    return Settings(
        PROJECT_ROOT=str(Path(__file__).parent.parent),
        TESTING=True
    )


@pytest.fixture
def client():
    """Test client fixture."""
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
