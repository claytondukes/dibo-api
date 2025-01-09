"""
Pytest fixtures for game data tests.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Sample metadata for testing."""
    return {
        "last_updated": "2025-01-05T16:49:39-05:00",
        "version": "1.0",
        "data_structure_version": "1.0"
    }


@pytest.fixture
def sample_gem() -> Dict[str, Any]:
    """Sample gem data for testing."""
    return {
        "Stars": 5,
        "Name": "Blood-Soaked Jade",
        "Base Effect": "Up to 8% increased damage",
        "Rank 10 Effect": "Increases all damage by 32%",
        "Owned Rank": 10,
        "Quality (if 5 star)": 5
    }


@pytest.fixture
def sample_gems_data() -> Dict[str, Any]:
    """Sample gems collection for testing."""
    return {
        "gems_by_skill": {
            "movement": [
                {
                    "Stars": 5,
                    "Name": "Blood-Soaked Jade",
                    "Base Effect": "Up to 8% increased damage",
                    "Rank 10 Effect": "Increases all damage by 32%",
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
def sample_equipment_set() -> Dict[str, Any]:
    """Sample equipment set data for testing."""
    return {
        "pieces": 6,
        "description": "A set focused on DoT damage",
        "bonuses": {
            "2": "Increases DoT damage by 15%",
            "4": "Additional DoT damage",
            "6": "Unleash lightning strikes"
        },
        "use_case": "Best for DoT builds"
    }


@pytest.fixture
def sample_equipment_sets_data() -> Dict[str, Any]:
    """Sample equipment sets collection for testing."""
    return {
        "metadata": {
            "bonus_thresholds": [2, 4, 6],
            "bonus_rules": "Set bonuses are additive"
        },
        "registry": {
            "Grace of the Flagellant": {
                "pieces": 6,
                "description": "A set focused on DoT damage",
                "bonuses": {
                    "2": "Increases DoT damage by 15%",
                    "4": "Additional DoT damage",
                    "6": "Unleash lightning strikes"
                },
                "use_case": "Best for DoT builds"
            }
        }
    }


@pytest.fixture
def sample_stat_value() -> Dict[str, Any]:
    """Sample stat value for testing."""
    return {
        "conditions": [],
        "value": 15.0,
        "unit": "percentage",
        "scaling": False
    }


@pytest.fixture
def sample_stat_source() -> Dict[str, Any]:
    """Sample stat source for testing."""
    return {
        "name": "Berserker's Eye",
        "stars": 1,
        "base_values": [
            {
                "conditions": [],
                "value": 8.0,
                "unit": "percentage",
                "scaling": False
            }
        ],
        "rank_10_values": [
            {
                "conditions": [],
                "value": 16.0,
                "unit": "percentage",
                "scaling": False
            }
        ],
        "conditions": [],
        "rank_10_conditions": []
    }


@pytest.fixture
def sample_stats_data() -> Dict[str, Any]:
    """Sample stats collection for testing."""
    return {
        "critical_hit_chance": {
            "gems": [
                {
                    "name": "Berserker's Eye",
                    "stars": 1,
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 8.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [
                        {
                            "conditions": [],
                            "value": 16.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ],
            "essences": []
        },
        "damage_increase": {
            "gems": [],
            "essences": []
        }
    }


@pytest.fixture
def mock_data_dir(
    tmp_path_factory: TempPathFactory,
    sample_metadata: Dict[str, Any],
    sample_gems_data: Dict[str, Any],
    sample_equipment_sets_data: Dict[str, Any],
    sample_stats_data: Dict[str, Any]
) -> Path:
    """Create a temporary data directory with mock files."""
    base_dir = tmp_path_factory.mktemp("data")
    
    # Create metadata file
    with open(base_dir / "metadata.json", "w") as f:
        json.dump(sample_metadata, f)
    
    # Create gems directory and file
    gems_dir = base_dir / "gems"
    gems_dir.mkdir()
    with open(gems_dir / "gem_skillmap.json", "w") as f:
        json.dump(sample_gems_data, f)
    
    # Create equipment directory and file
    equipment_dir = base_dir / "equipment"
    equipment_dir.mkdir()
    with open(equipment_dir / "sets.json", "w") as f:
        json.dump(sample_equipment_sets_data, f)
    
    # Create stats file
    with open(base_dir / "stats.json", "w") as f:
        json.dump(sample_stats_data, f)
    
    return base_dir
