"""Tests for build configuration schemas."""
import pytest
from pydantic import ValidationError

from api.models.game_data.schemas.builds.models import BuildConfig, BuildSummary
from api.models.game_data.schemas.equipment import EquipmentSlot
from api.models.game_data.schemas.gems import GemConfig
from api.models.game_data.schemas.stats import StatBlock


@pytest.fixture
def valid_build_data():
    """Fixture providing valid build configuration data."""
    return {
        "version": "1.0.0",
        "name": "Test Build",
        "class_type": "Warrior",
        "equipment": {
            EquipmentSlot.WEAPON: "mighty_sword",
            EquipmentSlot.ARMOR: "plate_mail"
        },
        "gems": {
            "socket_1": GemConfig(type="strength", level=1),
            "socket_2": GemConfig(type="vitality", level=2)
        },
        "stats": StatBlock(
            strength=10,
            dexterity=5,
            intelligence=3,
            vitality=7
        ),
        "description": "A test build configuration",
        "tags": ["pvp", "beginner"]
    }


def test_build_config_valid(valid_build_data):
    """Test that valid build data creates a BuildConfig successfully."""
    build = BuildConfig(**valid_build_data)
    assert build.version == "1.0.0"
    assert build.name == "Test Build"
    assert build.class_type == "Warrior"
    assert len(build.equipment) == 2
    assert len(build.gems) == 2
    assert build.stats.strength == 10
    assert build.description == "A test build configuration"
    assert "pvp" in build.tags


def test_build_config_missing_required():
    """Test that BuildConfig raises error when missing required fields."""
    with pytest.raises(ValidationError):
        BuildConfig(
            version="1.0.0",
            name="Test Build"
            # Missing required fields
        )


def test_build_config_invalid_name(valid_build_data):
    """Test that BuildConfig validates name length constraints."""
    invalid_data = dict(valid_build_data)
    invalid_data["name"] = ""  # Empty name should fail
    with pytest.raises(ValidationError):
        BuildConfig(**invalid_data)


def test_build_summary_valid():
    """Test that valid data creates a BuildSummary successfully."""
    summary_data = {
        "id": "build123",
        "version": "1.0.0",
        "name": "Test Build",
        "class_type": "Warrior",
        "tags": ["pvp"],
        "created_at": "2025-01-05T22:56:55-05:00",
        "updated_at": "2025-01-05T22:56:55-05:00"
    }
    summary = BuildSummary(**summary_data)
    assert summary.id == "build123"
    assert summary.version == "1.0.0"
    assert summary.name == "Test Build"
    assert summary.class_type == "Warrior"
    assert "pvp" in summary.tags
