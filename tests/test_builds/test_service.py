"""Test build generation service."""

import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from api.builds.models import BuildFocus, BuildType
from api.builds.service import BuildService


@pytest.fixture
def build_service():
    """Build service fixture."""
    return BuildService()


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary data directory with mock data files."""
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)
    
    # Create mock data files
    mock_data = {
        "synergies.json": {
            "critical_hit": {
                "gems": ["Berserker's Eye", "Cutthroat's Grin"],
                "essences": [],
                "skills": []
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
            },
            "essence_slots": {
                "total_required": 6,
                "unique": True
            }
        },
        "stats.json": {
            "critical_hit": {
                "base": 5.0,
                "max": 100.0
            }
        },
        "cross_references.json": {
            "gems": {
                "Berserker's Eye": ["critical_hit"]
            }
        },
        
        # Gem data
        "gems/progression.json": {
            "Berserker's Eye": {
                "ranks": [1, 2, 5, 10],
                "resonance": [10, 20, 50, 100]
            }
        },
        "gems/stat_boosts.json": {
            "critical_hit": {
                "Berserker's Eye": {
                    "rank_10": 2.0,
                    "scaling": True
                }
            }
        },
        "gems/synergies.json": {
            "critical_hit": ["Berserker's Eye", "Cutthroat's Grin"]
        },
        
        # Skill data
        "skills/registry.json": {
            "barbarian": {
                "Whirlwind": {
                    "type": "primary",
                    "damage_type": "physical"
                }
            }
        },
        
        # Essence data
        "essences/registry.json": {
            "barbarian": {
                "Whirlwind": {
                    "Gale Force": {
                        "type": "legendary",
                        "slot": "chest"
                    }
                }
            }
        },
        "essences/effects.json": {
            "barbarian": {
                "Whirlwind": {
                    "Gale Force": {
                        "critical_hit": 2.0
                    }
                }
            }
        },
        
        # Equipment data
        "equipment/sets.json": {
            "metadata": {
                "version": 1
            },
            "registry": {
                "Grace of the Flagellant": {
                    "pieces": ["chest", "legs"],
                    "bonuses": {
                        "2": {
                            "critical_hit": 1.5
                        }
                    },
                    "description": "A set for the barbarian"
                }
            }
        },
        
        # Class-specific data
        "classes/barbarian/base_skills.json": {
            "Whirlwind": {
                "base_type": "primary",
                "description": "A primary skill for the barbarian"
            }
        },
        "classes/barbarian/essences.json": {
            "Whirlwind": {
                "Gale Force": {
                    "type": "legendary",
                    "slot": "chest"
                }
            }
        },
        "classes/barbarian/essence_registry.json": {
            "Gale Force": {
                "type": "legendary",
                "slot": "chest"
            }
        },
        "classes/barbarian/constraints.json": {
            "essence_slots": {
                "total_required": 6,
                "unique": True
            }
        }
    }
    
    # Write mock data files
    for filename, data in mock_data.items():
        file_path = data_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f)
    
    return data_dir


def test_load_indexed_data(build_service):
    """Test that all required data files are loaded."""
    # Check that required data is loaded
    assert build_service.synergies is not None
    assert build_service.constraints is not None
    assert build_service.stats is not None
    assert build_service.cross_references is not None
    
    # Check gem data
    assert build_service.gems_data is not None
    assert "progression" in build_service.gems_data
    assert "stat_boosts" in build_service.gems_data
    assert "synergies" in build_service.gems_data
    
    # Check skill data
    assert build_service.skills_data is not None
    assert "registry" in build_service.skills_data
    
    # Check essence data
    assert build_service.essences_data is not None
    assert "registry" in build_service.essences_data
    assert "effects" in build_service.essences_data
    
    # Check equipment data
    assert build_service.equipment_data is not None
    assert "sets" in build_service.equipment_data
    
    # Check class-specific data
    assert build_service.class_data is not None
    assert "barbarian" in build_service.class_data
    assert "base_skills" in build_service.class_data["barbarian"]
    assert "essences" in build_service.class_data["barbarian"]
    assert "essence_registry" in build_service.class_data["barbarian"]
    assert "constraints" in build_service.class_data["barbarian"]


def test_missing_class_data(mock_data_dir):
    """Test handling of missing class-specific data."""
    # Remove class-specific data file
    class_file = mock_data_dir / "classes" / "barbarian" / "base_skills.json"
    class_file.unlink()
    
    # Service should raise error when class data is missing
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    assert "Required class data file not found" in str(exc_info.value.detail)


def test_invalid_class_data_format(mock_data_dir):
    """Test handling of invalid class-specific data format."""
    # Write invalid data to class file
    class_file = mock_data_dir / "classes" / "barbarian" / "base_skills.json"
    with open(class_file, "w") as f:
        json.dump({
            "InvalidFormat": {  # Wrong top-level key
                "Gale Force": {
                    "type": "legendary",
                    "slot": "chest"
                }
            }
        }, f)
    
    # Service should raise error for invalid data format
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    assert "Error loading data files" in str(exc_info.value.detail)


def test_empty_class_data(mock_data_dir):
    """Test handling of empty class-specific data."""
    # Write empty data to class file
    class_file = mock_data_dir / "classes" / "barbarian" / "base_skills.json"
    with open(class_file, "w") as f:
        json.dump({}, f)
    
    # Service should load successfully but class data should be empty
    service = BuildService(data_dir=mock_data_dir)
    assert service.class_data["barbarian"]["base_skills"] == {}


def test_class_data_references(mock_data_dir):
    """Test that class-specific data references valid skills and essences."""
    # Add a skill mapping for a non-existent skill
    class_file = mock_data_dir / "classes" / "barbarian" / "base_skills.json"
    with open(class_file, "w") as f:
        json.dump({
            "NonExistentSkill": {  # This skill doesn't exist in skills/registry.json
                "base_type": "primary",
                "description": "A primary skill for the barbarian"
            }
        }, f)
    
    # Service should raise error for invalid skill reference
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    assert "Error loading data files" in str(exc_info.value.detail)


def test_class_data_consistency(mock_data_dir):
    """Test consistency between class data and core data files."""
    service = BuildService(data_dir=mock_data_dir)
    
    # Get Whirlwind skill mapping
    skill_mapping = service.class_data["barbarian"]["base_skills"]["Whirlwind"]
    
    # Verify skill exists in registry
    assert "Whirlwind" in service.skills_data["registry"]["barbarian"]
    
    # Verify essence exists in registry
    assert "Gale Force" in service.class_data["barbarian"]["essences"]["Whirlwind"]
    assert "Gale Force" in service.essences_data["registry"]["barbarian"]["Whirlwind"]
    
    # Verify essence effects match
    essence_name = "Gale Force"
    essence_effects = service.essences_data["effects"]["barbarian"]["Whirlwind"][essence_name]
    assert essence_effects["critical_hit"] == 2.0


def test_class_data_structure(mock_data_dir):
    """Test the structure of class-specific data."""
    service = BuildService(data_dir=mock_data_dir)
    
    # Check barbarian class data structure
    assert "barbarian" in service.class_data
    barbarian_data = service.class_data["barbarian"]
    
    # Check base skills
    assert "base_skills" in barbarian_data
    assert isinstance(barbarian_data["base_skills"], dict)
    
    # Check skill data
    skill_data = barbarian_data["base_skills"]["Whirlwind"]
    assert isinstance(skill_data, dict)
    assert "base_type" in skill_data
    assert "description" in skill_data
    
    # Check essences
    assert "essences" in barbarian_data
    assert isinstance(barbarian_data["essences"], dict)
    
    # Check essence registry
    assert "essence_registry" in barbarian_data
    assert isinstance(barbarian_data["essence_registry"], dict)


@pytest.mark.parametrize("invalid_data", [
    # Missing required files
    {"missing": ["classes/barbarian/base_skills.json"]},
    {"missing": ["classes/barbarian/essences.json"]},
    {"missing": ["classes/barbarian/essence_registry.json"]},
    {"missing": ["classes/barbarian/constraints.json"]},
    
    # Invalid file formats
    {"invalid": ["classes/barbarian/base_skills.json"]},
    {"invalid": ["classes/barbarian/essences.json"]},
    {"invalid": ["classes/barbarian/essence_registry.json"]},
    {"invalid": ["classes/barbarian/constraints.json"]}
])
def test_class_data_validation(mock_data_dir, invalid_data):
    """Test validation of class-specific data with various invalid formats."""
    # Write invalid data to class file
    if "missing" in invalid_data:
        for filename in invalid_data["missing"]:
            file_path = mock_data_dir / filename
            file_path.unlink()
    elif "invalid" in invalid_data:
        for filename in invalid_data["invalid"]:
            file_path = mock_data_dir / filename
            with open(file_path, "w") as f:
                json.dump({}, f)
    
    # Service should raise error for invalid data
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    assert "Error loading data files" in str(exc_info.value.detail)


def test_validate_data_structure(build_service):
    """Test that loaded data has the expected structure."""
    # Check synergies structure
    assert isinstance(build_service.synergies, dict)
    for category in build_service.synergies.values():
        assert "gems" in category
        assert "essences" in category
        assert "skills" in category
    
    # Check constraints structure
    assert "gem_slots" in build_service.constraints
    assert "total_required" in build_service.constraints["gem_slots"]
    assert "primary" in build_service.constraints["gem_slots"]


def test_missing_required_file(mock_data_dir):
    """Test handling of missing required data files."""
    # Remove a required file
    (mock_data_dir / "constraints.json").unlink()
    
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    
    assert exc_info.value.status_code == 500
    assert "Missing required data file" in str(exc_info.value.detail)


def test_invalid_json_file(mock_data_dir):
    """Test handling of invalid JSON files."""
    # Write invalid JSON
    with open(mock_data_dir / "synergies.json", "w") as f:
        f.write("invalid json content")
    
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    
    assert exc_info.value.status_code == 500
    assert "Failed to parse data file" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_build_basic(build_service):
    """Test basic build generation without inventory."""
    response = await build_service.generate_build(
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS
    )
    
    assert response.build is not None
    assert response.stats is not None
    assert isinstance(response.recommendations, list)


@pytest.mark.asyncio
async def test_generate_build_with_inventory(build_service):
    """Test build generation with inventory."""
    inventory = {
        "Berserker's Eye": {
            "owned_rank": 10,
            "quality": None
        }
    }
    
    response = await build_service.generate_build(
        build_type=BuildType.PVP,
        focus=BuildFocus.SURVIVAL,
        inventory=inventory
    )
    
    assert response.build is not None
    assert response.stats is not None
    assert isinstance(response.recommendations, list)
    # TODO: Add assertions for inventory-specific recommendations
