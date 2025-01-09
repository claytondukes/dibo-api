"""Test configuration and fixtures."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.core.config import Settings, get_settings
from api.main import app
from api.models.game_data.data_manager import GameDataManager


def get_settings_override() -> Settings:
    """Override settings for testing."""
    return Settings(
        app_name="Test API",
        admin_email="test@example.com",
        items_per_user=50,
        database_url="sqlite:///./test.db",
        redis_url="redis://localhost",
    )


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings fixture."""
    return get_settings_override()


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Get the path to the indexed data directory."""
    return Path(__file__).parent.parent / "data" / "indexed"


@pytest.fixture(scope="session")
def data_manager(data_dir: Path) -> GameDataManager:
    """Create a GameDataManager instance with test data."""
    return GameDataManager(data_dir)


@pytest.fixture
def client(data_manager, test_settings: Settings) -> TestClient:
    """Create a test client with the data manager."""
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.state.data_manager = data_manager
    return TestClient(app)


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "last_updated": "2025-01-05T16:49:39-05:00",
        "version": "1.0",
        "data_structure_version": "1.0"
    }


@pytest.fixture
def sample_gem():
    """Sample gem data for testing."""
    return {
        "Stars": 5,
        "Name": "Blood-Soaked Jade",
        "Base Effect": "Increases all damage you deal by up to 8%",
        "Rank 10 Effect": "Increases all damage you deal by up to 24% while at full Life",
        "Owned Rank": 10,
        "Quality (if 5 star)": 5
    }


@pytest.fixture
def sample_gems_data():
    """Sample gems data for testing."""
    return {
        "gems_by_skill": {
            "movement": [
                {
                    "Stars": 5,
                    "Name": "Blood-Soaked Jade",
                    "Base Effect": "Increases all damage you deal by up to 8%",
                    "Rank 10 Effect": "Increases all damage you deal by up to 24% while at full Life",
                    "Owned Rank": 10,
                    "Quality (if 5 star)": 5
                }
            ],
            "primary attack": [],
            "attack": [],
            "summon": [],
            "channeled": []
        }
    }


@pytest.fixture
def sample_equipment_set():
    """Sample equipment set data for testing."""
    return {
        "pieces": 6,
        "description": "A set focused on DoT damage",
        "bonuses": {
            "2": "Increases DoT damage by 15%",
            "4": "Additional DoT damage",
            "6": "Unleash lightning strikes"
        }
    }


@pytest.fixture
def sample_equipment_sets_data():
    """Sample equipment sets data for testing."""
    return {
        "sets": [
            {
                "name": "Grace of the Flagellant",
                "pieces": 6,
                "description": "A set focused on DoT damage",
                "bonuses": {
                    "2": "Increases DoT damage by 15%",
                    "4": "Additional DoT damage",
                    "6": "Unleash lightning strikes"
                }
            }
        ]
    }


@pytest.fixture
def sample_stat_value():
    """Sample stat value data for testing."""
    return {
        "value": 15.0,
        "unit": "percentage",
        "scaling": False,
        "conditions": []
    }


@pytest.fixture
def sample_stat_source():
    """Sample stat source data for testing."""
    return {
        "source": "Berserker's Eye",
        "value": 15.0
    }


@pytest.fixture
def sample_stats_data():
    """Sample game stats data for testing."""
    return {
        "stats": [
            {
                "name": "Critical Hit Chance",
                "description": "Chance to deal critical damage",
                "base_value": 5.0,
                "unit": "percentage"
            }
        ]
    }
