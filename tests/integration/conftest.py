"""Shared fixtures for integration tests."""
from pathlib import Path

import pytest

from api.models.game_data.data_manager import GameDataManager


@pytest.fixture
def data_manager() -> GameDataManager:
    """Create a GameDataManager instance for testing."""
    base_path = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed")
    return GameDataManager(base_path=base_path)
