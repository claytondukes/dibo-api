"""Test fixtures for game API tests."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from api.main import app
from api.core.config import settings


@pytest.fixture
def data_dir() -> Path:
    """Get the path to the indexed data directory."""
    return Path(settings.PROJECT_ROOT) / "data" / "indexed"


@pytest.fixture
def client(data_dir: Path) -> TestClient:
    """Create a test client using the real data directory."""
    return TestClient(app)
