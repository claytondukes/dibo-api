"""Test fixtures for game API tests."""

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.core.config import settings


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary data directory with test data."""
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)

    # Create test metadata
    metadata = {
        "version": "1.0.0",
        "data_structure_version": "1.0.0",
        "last_updated": "2025-01-05T17:10:00Z",
        "categories": ["gems", "equipment_sets", "stats"]
    }
    with open(data_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)

    # Create test gem data
    gems_dir = data_dir / "gems"
    gems_dir.mkdir(parents=True)
    
    gems_data = {
        "gems_by_skill": {
            "movement": [
                {
                    "Name": "Blood-Soaked Jade",
                    "Stars": 5,
                    "Base Effect": "Increases movement speed by 10%",
                    "Rank 10 Effect": "Increases movement speed by 20%"
                }
            ],
            "primary attack": [],
            "attack": [],
            "summon": [],
            "channeled": []
        }
    }
    with open(gems_dir / "gem_skillmap.json", "w") as f:
        json.dump(gems_data, f)

    # Create equipment sets data
    equipment_dir = data_dir / "equipment"
    equipment_dir.mkdir(parents=True)
    
    equipment_data = {
        "metadata": {
            "version": "1.0.0",
            "data_structure_version": "1.0.0",
            "last_updated": "2025-01-05T17:10:00Z",
            "bonus_thresholds": [2, 4, 6],
            "bonus_rules": "Bonuses are cumulative"
        },
        "registry": {}
    }
    with open(equipment_dir / "sets.json", "w") as f:
        json.dump(equipment_data, f)

    # Create empty stats data
    stats_data = {
        "critical_hit_chance": {},
        "damage_increase": {},
        "attack_speed": {},
        "movement_speed": {},
        "life": {}
    }
    with open(data_dir / "stats.json", "w") as f:
        json.dump(stats_data, f)

    yield data_dir
    shutil.rmtree(data_dir.parent)


@pytest.fixture
def override_data_dir(monkeypatch, test_data_dir):
    """Override the project root to use test data directory."""
    monkeypatch.setattr(settings, "PROJECT_ROOT", test_data_dir.parent.parent)


@pytest.fixture
def client(override_data_dir):
    """Test client with overridden data directory."""
    return TestClient(app)
