"""Test configuration and fixtures."""

import os
import pytest
from pathlib import Path

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

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment."""
    yield
