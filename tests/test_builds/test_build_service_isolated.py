"""Test build generation service in isolation."""

import json
from pathlib import Path

import pytest

# Import directly from the builds package
from api.builds.models import BuildFocus, BuildType
from api.builds.service import BuildService

# Test data directory is set in conftest.py


@pytest.fixture
def build_service(tmp_path):
    """Build service fixture."""
    # Create test data directory
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)
    
    # Create minimal test data
    test_data = {
        "synergies.json": {
            "critical_hit": {
                "gems": ["Berserker's Eye"],
                "essences": [],
                "skills": []
            }
        },
        "stats.json": {
            "critical_hit": {
                "base": 5.0,
                "max": 100.0
            }
        },
        "constraints.json": {
            "gem_slots": {
                "total_required": 8,
                "primary": {
                    "required": 8,
                    "unique": True,
                    "star_ratings": [1, 2, 5]
                }
            }
        },
        "gems/progression.json": {
            "metadata": {"version": "1.0"},
            "gems": {
                "Berserker's Eye": {
                    "ranks": [1, 2, 5, 10],
                    "resonance": [10, 20, 50, 100]
                }
            }
        },
        "gems/stat_boosts.json": {
            "metadata": {"version": "1.0"},
            "stats": {
                "critical_hit": {
                    "Berserker's Eye": {
                        "rank_10": 2.0,
                        "scaling": True
                    }
                }
            }
        },
        "gems/synergies.json": {
            "metadata": {"version": "1.0"},
            "synergies": {
                "critical_hit": ["Berserker's Eye"]
            }
        },
        "gems/gems.json": {
            "metadata": {"version": "1.0"},
            "effects": {
                "Berserker's Eye": {
                    "critical_hit": "2.0%",
                    "type": "legendary",
                    "slot": "primary"
                }
            }
        },
        "equipment/sets.json": {
            "metadata": {"version": "1.0"},
            "sets": {}
        },
        "classes/barbarian/base_skills.json": {
            "metadata": {"version": "1.0"},
            "Whirlwind": {
                "base_type": "primary",
                "description": "A primary skill for the barbarian"
            }
        },
        "classes/barbarian/essences.json": {
            "metadata": {"version": "1.0"},
            "essences": {
                "Whirlwind": {
                    "Gale Force": {
                        "type": "legendary",
                        "slot": "chest",
                        "effect": "critical_hit:2.0%"
                    }
                }
            },
            "indexes": {
                "by_slot": {
                    "chest": ["Gale Force"]
                },
                "by_skill": {
                    "Whirlwind": ["Gale Force"]
                }
            }
        },
        "classes/barbarian/constraints.json": {
            "essence_slots": {
                "total_required": 6,
                "unique": True
            }
        }
    }
    
    # Write test data files
    for filename, data in test_data.items():
        file_path = data_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f)
    
    return BuildService(data_dir=data_dir)


def test_load_indexed_data(build_service):
    """Test that all required data files are loaded."""
    # Check that required data is loaded
    assert build_service.synergies is not None
    assert build_service.constraints is not None
    assert build_service.stats is not None
    
    # Check gem data
    assert build_service.gem_data is not None
    assert "progression" in build_service.gem_data
    assert "stat_boosts" in build_service.gem_data
    assert "synergies" in build_service.gem_data
    assert "effects" in build_service.gem_data
    
    # Check equipment data
    assert build_service.equipment_data is not None
    assert "sets" in build_service.equipment_data
    
    # Check class-specific data
    assert build_service.class_data is not None
    assert "barbarian" in build_service.class_data
    assert "base_skills" in build_service.class_data["barbarian"]
    assert "essences" in build_service.class_data["barbarian"]


def test_class_data_consistency(build_service):
    """Test consistency between class data and core data files."""
    # Get Whirlwind skill mapping
    skill_mapping = build_service.class_data["barbarian"]["base_skills"]["Whirlwind"]
    assert skill_mapping["base_type"] == "primary"
    
    # Verify essence exists in class data
    essence_data = build_service.class_data["barbarian"]["essences"]
    assert "Whirlwind" in essence_data["essences"]
    assert "Gale Force" in essence_data["essences"]["Whirlwind"]
