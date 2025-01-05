"""Test build generation service."""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

from fastapi import HTTPException

from api.builds.service import BuildService
from api.builds.models import BuildType, BuildFocus, Gem, Skill, Equipment

@pytest.fixture
def base_test_data() -> Dict[str, Any]:
    """Base test data fixture with minimal required data."""
    return {
        "equipment.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "sets": {
                "test_set": {
                    "pieces": {"test_weapon": {"type": "two_handed_axe", "stats": {"damage": 100}}},
                    "bonuses": {
                        "2": {"critical_hit": 1.5}
                    }
                }
            },
            "gear": {
                "test_weapon": {
                    "type": "two_handed_axe",
                    "stats": {
                        "damage": 100,
                        "critical_hit": 5
                    }
                }
            }
        },
        "stats.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 2
            },
            "stats": {
                "critical_hit": {
                    "base": 5.0,
                    "max": 100.0,
                    "categories": ["damage", "critical"]
                },
                "attack_speed": {
                    "base": 100.0,
                    "max": 200.0,
                    "categories": ["damage"]
                }
            }
        },
        "synergies.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 1
            },
            "synergies": {
                "critical_hit": {
                    "gems": ["test_aux_gem"],
                    "essences": ["test_essence"],
                    "skills": ["Whirlwind"],
                    "conditions": {
                        "test_aux_gem": []
                    }
                }
            }
        },
        "cross_references.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 3
            },
            "references": {
                "gems": {
                    "test_gem": {
                        "type": "primary",
                        "stats": ["critical_hit"]
                    },
                    "test_aux_gem": {
                        "type": "auxiliary",
                        "stats": ["critical_hit"]
                    }
                },
                "essences": {
                    "Gale Force": {
                        "type": "legendary",
                        "stats": ["critical_hit"]
                    }
                },
                "skills": {
                    "Whirlwind": {
                        "type": "primary",
                        "stats": ["critical_hit"]
                    }
                }
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
            },
            "required_categories": {
                "aoe": 2,
                "control": 1
            }
        },
        "gems/progression.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "progression": {
                "Berserker's Eye": {
                    "stars": 1,
                    "ranks": {
                        "1": {
                            "effects": [],
                            "stats": {
                                "critical_hit_chance": 2.0
                            }
                        }
                    }
                }
            }
        },
        "gems/stat_boosts.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "stat_boosts": {
                "critical_hit_chance": {
                    "gems": ["Berserker's Eye"],
                    "essences": []
                }
            }
        },
        "gems/synergies.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "synergies": [
                {
                    "name": "critical_hit",
                    "gems": ["Berserker's Eye"],
                    "essences": [],
                    "skills": []
                }
            ]
        },
        "gems/gems.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "gems": {
                "Berserker's Eye": {
                    "name": "Berserker's Eye",
                    "effects": ["Increases critical hit chance"]
                }
            }
        },
        "classes/barbarian/base_skills.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 16
            },
            "skills": {
                "Whirlwind": {
                    "name": "Whirlwind",
                    "base_type": "damage",
                    "second_base_type": "channel",
                    "categories": ["damage", "aoe"],
                    "cooldown": 0.5,
                    "slot": "primary"
                }
            }
        },
        "classes/barbarian/essences.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 1
            },
            "essences": {
                "Whirlwind": {
                    "Gale Force": {
                        "type": "legendary",
                        "slot": "chest"
                    }
                }
            },
            "indexes": {
                "by_type": {
                    "legendary": ["Gale Force"]
                },
                "by_slot": {
                    "chest": ["Gale Force"]
                }
            }
        },
        "classes/barbarian/constraints.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04",
                "total_count": 1
            },
            "constraints": {
                "weapon_types": ["frenzy", "lacerate"],
                "skill_slots": {
                    "available_skills": [
                        "Hammer of the Ancients",
                        "Cleave",
                        "Whirlwind",
                        "Sprint",
                        "Wrath of the Berserker",
                        "Undying Rage",
                        "Ground Stomp",
                        "Leap",
                        "Furious Charge",
                        "Chained Spear",
                        "Demoralize",
                        "Grab",
                        "Sunder"
                    ],
                    "max_skills": 4
                }
            }
        },
        "skills.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 16
            },
            "registry": {
                "barbarian": {
                    "Whirlwind": {
                        "name": "Whirlwind",
                        "base_type": "damage",
                        "second_base_type": "channel",
                        "categories": ["damage", "aoe"],
                        "cooldown": 0.5,
                        "slot": "primary"
                    },
                    "Ground Stomp": {
                        "name": "Ground Stomp",
                        "base_type": "control",
                        "second_base_type": "charge",
                        "categories": ["control", "aoe"],
                        "cooldown": 9,
                        "slot": "secondary"
                    }
                }
            }
        }
    }

@pytest.fixture
def mock_data_dir(tmp_path, base_test_data):
    """Create a temporary data directory with mock data files."""
    indexed_dir = tmp_path / "data" / "indexed"
    indexed_dir.mkdir(parents=True)

    # Create required directories
    (indexed_dir / "gems").mkdir()
    (indexed_dir / "equipment").mkdir()
    (indexed_dir / "classes" / "barbarian").mkdir(parents=True)

    # Write all files from base_test_data
    for filename, content in base_test_data.items():
        file_path = indexed_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(content, f)

    return indexed_dir

@pytest.fixture
def build_service(mock_data_dir):
    """Build service fixture."""
    return BuildService(data_dir=mock_data_dir)


def test_load_indexed_data(build_service):
    """Test that all required data files are loaded."""
    # Check that required data is loaded
    assert build_service.synergies is not None
    assert build_service.constraints is not None
    assert build_service.stats is not None
    assert build_service.cross_references is not None
    
    # Check gem data
    assert build_service.gem_data is not None
    assert "progression" in build_service.gem_data
    assert "stat_boosts" in build_service.gem_data
    assert "synergies" in build_service.gem_data
    
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
    skill_mapping = service.class_data["barbarian"]["base_skills"]["skills"]["Whirlwind"]
    assert skill_mapping is not None
    assert skill_mapping["base_type"] == "damage"
    assert skill_mapping["categories"] == ["damage", "aoe"]
    
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
    skill_data = barbarian_data["base_skills"]["skills"]["Whirlwind"]
    assert skill_data is not None
    assert "base_type" in skill_data
    assert "categories" in skill_data
    
    # Check essences
    assert "essences" in barbarian_data
    assert isinstance(barbarian_data["essences"], dict)


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
            if file_path.exists():
                file_path.unlink()
    elif "invalid" in invalid_data:
        for filename in invalid_data["invalid"]:
            file_path = mock_data_dir / filename
            if filename.endswith("base_skills.json"):
                with open(file_path, "w") as f:
                    json.dump({
                        "metadata": {
                            "version": "1.0",
                            "last_updated": "2025-01-05"
                        }
                        # Missing "skills" key
                    }, f)
            else:
                with open(file_path, "w") as f:
                    json.dump({}, f)

    # Service should raise error for invalid data
    with pytest.raises(HTTPException) as exc_info:
        BuildService(data_dir=mock_data_dir)
    assert "Missing required keys" in str(exc_info.value.detail)


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


@pytest.mark.asyncio
async def test_build_specific_requirements(mock_data_dir):
    """Test that builds respect class, type and focus specific requirements."""
    # Create required directories
    (mock_data_dir / "gems").mkdir(exist_ok=True)
    (mock_data_dir / "equipment").mkdir(exist_ok=True)
    (mock_data_dir / "classes" / "barbarian").mkdir(parents=True, exist_ok=True)

    # Create required gem files
    gem_files = {
        "gems/gems.json": {
            "gems_by_skill": {
                "damage": [
                    {
                        "Stars": "2",
                        "Name": "test_gem",
                        "Base Effect": "Increases damage by 10%",
                        "Rank 10 Effect": "Increases damage by 20% and grants additional effects",
                        "Rank": "1",
                        "Quality (if 5 star)": None
                    }
                ],
                "critical": [
                    {
                        "Stars": "2",
                        "Name": "test_aux_gem",
                        "Base Effect": "Increases critical hit chance",
                        "Rank 10 Effect": "Greatly increases critical hit chance",
                        "Rank": "1",
                        "Quality (if 5 star)": None
                    }
                ]
            },
            "synergies": {}
        },
        "gems/progression.json": {
            "test_gem": {
                "stars": "2",
                "ranks": {
                    "1": {
                        "effects": [
                            {
                                "type": "stat_effect",
                                "text": "Increases damage by 10%",
                                "conditions": []
                            }
                        ],
                        "stats": {
                            "damage_increase": [
                                {
                                    "value": 10.0,
                                    "conditions": [],
                                    "context": "damage increase"
                                }
                            ]
                        }
                    }
                },
                "max_rank": 10,
                "magic_find": "10",
                "max_effect": "Increases damage by 20% and grants additional effects"
            },
            "test_aux_gem": {
                "stars": "2",
                "ranks": {
                    "1": {
                        "effects": [
                            {
                                "type": "stat_effect",
                                "text": "Increases critical hit chance",
                                "conditions": []
                            }
                        ],
                        "stats": {
                            "critical_hit_chance": [
                                {
                                    "value": 5.0,
                                    "conditions": [],
                                    "context": "critical hit chance"
                                }
                            ]
                        }
                    }
                },
                "max_rank": 10,
                "magic_find": "10",
                "max_effect": "Greatly increases critical hit chance"
            }
        },
        "gems/stat_boosts.json": {
            "critical_hit_chance": {
                "gems": [
                    {
                        "name": "test_aux_gem",
                        "stars": "2",
                        "base_values": [
                            {
                                "conditions": [],
                                "value": 5.0,
                                "unit": "percentage",
                                "scaling": False
                            }
                        ],
                        "rank_10_values": [
                            {
                                "conditions": [],
                                "value": 10.0,
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
                "gems": [
                    {
                        "name": "test_gem",
                        "stars": "2",
                        "base_values": [
                            {
                                "conditions": [],
                                "value": 10.0,
                                "unit": "percentage",
                                "scaling": False
                            }
                        ],
                        "rank_10_values": [
                            {
                                "conditions": [],
                                "value": 20.0,
                                "unit": "percentage",
                                "scaling": False
                            }
                        ],
                        "conditions": [],
                        "rank_10_conditions": []
                    }
                ],
                "essences": []
            }
        },
        "gems/synergies.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05"
            },
            "synergies": {
                "critical_hit": {
                    "gems": ["test_aux_gem"],
                    "essences": [],
                    "skills": ["Whirlwind"],
                    "conditions": {
                        "test_aux_gem": []
                    }
                },
                "damage_boost": {
                    "gems": ["test_gem"],
                    "essences": [],
                    "skills": ["Whirlwind"],
                    "conditions": {
                        "test_gem": []
                    }
                }
            }
        }
    }
    for filename, content in gem_files.items():
        with open(mock_data_dir / filename, "w") as f:
            json.dump(content, f)

    # Create required equipment files
    equipment_data = {
        "metadata": {
            "version": "1.0",
            "last_updated": "2025-01-04",
            "total_count": 1
        },
        "sets": {
            "test_set": {
                "pieces": {"test_weapon": {"type": "two_handed_axe", "stats": {"damage": 100}}},
                "bonuses": {
                    "2": {
                        "critical_hit": 1.5
                    }
                }
            }
        },
        "gear": {
            "test_weapon": {
                "type": "two_handed_axe",
                "stats": {
                    "damage": 100,
                    "critical_hit": 5
                }
            }
        }
    }
    with open(mock_data_dir / "equipment.json", "w") as f:
        json.dump(equipment_data, f)

    # Set up test data
    barbarian_constraints = {
        "weapon_types": ["frenzy", "lacerate"],
        "skill_slots": {
            "available_skills": [
                "Hammer of the Ancients",
                "Cleave",
                "Whirlwind",
                "Sprint",
                "Wrath of the Berserker",
                "Undying Rage",
                "Ground Stomp",
                "Leap",
                "Furious Charge",
                "Chained Spear",
                "Demoralize",
                "Grab",
                "Sunder"
            ],
            "max_skills": 4
        },
        "weapon_slots": {
            "available_weapons": [
                "Frenzy",
                "Lacerate"
            ]
        },
        "skill_categories": ["damage", "control", "buff"],
        "required_categories": {
            "damage": 1,
            "buff": 1
        }
    }
    
    # Add class constraints and data
    class_dir = mock_data_dir / "classes" / "barbarian"
    with open(class_dir / "constraints.json", "w") as f:
        json.dump(barbarian_constraints, f)

    # Add class skills and essences
    class_data = {
        "base_skills.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 16
            },
            "skills": {
                "Whirlwind": {
                    "name": "Whirlwind",
                    "base_type": "damage",
                    "second_base_type": "channel",
                    "categories": ["damage", "aoe"],
                    "cooldown": 0.5,
                    "slot": "primary"
                },
                "Ground Stomp": {
                    "name": "Ground Stomp",
                    "base_type": "control",
                    "second_base_type": "charge",
                    "categories": ["control", "aoe"],
                    "cooldown": 9,
                    "slot": "secondary"
                },
                "Cleave": {
                    "name": "Cleave",
                    "base_type": "damage",
                    "second_base_type": None,
                    "categories": ["damage", "aoe"],
                    "cooldown": 6,
                    "slot": "primary"
                },
                "Hammer of the Ancients": {
                    "name": "Hammer of the Ancients",
                    "base_type": "damage",
                    "second_base_type": None,
                    "categories": ["damage", "aoe"],
                    "cooldown": 9,
                    "slot": "primary"
                },
                "Sprint": {
                    "name": "Sprint",
                    "base_type": "buff",
                    "second_base_type": None,
                    "categories": ["buff", "mobility"],
                    "cooldown": 10,
                    "slot": "secondary"
                },
                "Wrath of the Berserker": {
                    "name": "Wrath of the Berserker",
                    "base_type": "buff",
                    "second_base_type": None,
                    "categories": ["buff"],
                    "cooldown": 25,
                    "slot": "secondary"
                },
                "Undying Rage": {
                    "name": "Undying Rage",
                    "base_type": "buff",
                    "second_base_type": None,
                    "categories": ["buff", "survival"],
                    "cooldown": 30,
                    "slot": "secondary"
                },
                "Leap": {
                    "name": "Leap",
                    "base_type": "control",
                    "second_base_type": "dash",
                    "categories": ["control", "mobility"],
                    "cooldown": 9,
                    "slot": "secondary"
                },
                "Furious Charge": {
                    "name": "Furious Charge",
                    "base_type": "dash",
                    "second_base_type": None,
                    "categories": ["mobility", "damage"],
                    "cooldown": 9,
                    "slot": "secondary"
                },
                "Demoralize": {
                    "name": "Demoralize",
                    "base_type": "control",
                    "second_base_type": None,
                    "categories": ["control", "aoe"],
                    "cooldown": 12,
                    "slot": "secondary"
                },
                "Grab": {
                    "name": "Grab",
                    "base_type": "control",
                    "second_base_type": "multiple-stage",
                    "categories": ["control"],
                    "cooldown": 7,
                    "slot": "secondary"
                },
                "Sunder": {
                    "name": "Sunder",
                    "base_type": "dash",
                    "second_base_type": None,
                    "categories": ["mobility", "damage", "aoe"],
                    "cooldown": 12,
                    "slot": "secondary"
                },
                "Chained Spear": {
                    "name": "Chained Spear",
                    "base_type": "control",
                    "second_base_type": "multiple-stage",
                    "categories": ["control", "damage"],
                    "cooldown": 8,
                    "slot": "secondary"
                },
                "Frenzy": {
                    "name": "Frenzy",
                    "base_type": "damage",
                    "second_base_type": None,
                    "categories": ["damage", "melee"],
                    "cooldown": 0,
                    "slot": "primary"
                },
                "Lacerate": {
                    "name": "Lacerate",
                    "base_type": "damage",
                    "second_base_type": None,
                    "categories": ["damage", "melee"],
                    "cooldown": 0,
                    "slot": "primary"
                }
            }
        },
        "essences.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 1
            },
            "essences": {
                "Whirlwind": {
                    "Gale Force": {
                        "type": "legendary",
                        "slot": "chest"
                    }
                }
            },
            "indexes": {
                "by_type": {
                    "legendary": ["Gale Force"]
                },
                "by_slot": {
                    "chest": ["Gale Force"]
                }
            }
        },
        "essence_registry.json": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-05",
                "total_count": 1
            },
            "essences": {
                "Gale Force": {
                    "type": "legendary",
                    "slot": "chest"
                }
            }
        },
        "constraints.json": {
            "essence_slots": {
                "total_required": 6,
                "unique": True
            }
        }
    }
    for filename, content in class_data.items():
        with open(class_dir / filename, "w") as f:
            json.dump(content, f)
    
    # Add build type constraints to main constraints
    constraints = {
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
        },
        "build_types": {
            "pve": {
                "required_categories": {
                    "aoe": 2,
                    "control": 1
                },
                "incompatible_skills": {
                    "dps": [
                        ["Whirlwind", "Undying Rage"],  # Survival skills reduce DPS optimization
                        ["Cleave", "Undying Rage"]      # Survival skills reduce DPS optimization
                    ]
                }
            },
            "pvp": {
                "required_categories": {
                    "control": 2
                },
                "incompatible_skills": {
                    "dps": [
                        ["Whirlwind", "Undying Rage"],  # Survival skills reduce DPS optimization
                        ["Cleave", "Undying Rage"]      # Survival skills reduce DPS optimization
                    ]
                }
            }
        }
    }
    
    with open(mock_data_dir / "constraints.json", "w") as f:
        json.dump(constraints, f)

    # Add synergies data
    synergies = {
        "metadata": {
            "version": "1.0",
            "last_updated": "2025-01-05"
        },
        "synergies": {
            "critical_hit": {
                "gems": ["test_aux_gem"],
                "essences": ["test_essence"],
                "skills": ["Whirlwind"],
                "conditions": {
                    "test_aux_gem": []
                }
            }
        }
    }
    with open(mock_data_dir / "synergies.json", "w") as f:
        json.dump(synergies, f)

    # Add stats data
    stats = {
        "metadata": {
            "version": "1.0",
            "last_updated": "2025-01-05",
            "total_count": 2
        },
        "stats": {
            "critical_hit": {
                "base": 5.0,
                "max": 100.0,
                "categories": ["damage", "critical"]
            },
            "attack_speed": {
                "base": 100.0,
                "max": 200.0,
                "categories": ["damage"]
            }
        }
    }
    with open(mock_data_dir / "stats.json", "w") as f:
        json.dump(stats, f)
    
    # Initialize service with test data
    service = BuildService(data_dir=mock_data_dir)
    
    # Test PvE build requirements
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_build(
            build_type=BuildType.PVE,
            focus=BuildFocus.DPS,
            character_class="barbarian"
        )
    assert "Required skill categories not met for build type" in str(exc_info.value.detail)
    
    # Test PvP build requirements
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_build(
            build_type=BuildType.PVP,
            focus=BuildFocus.DPS,
            character_class="barbarian"
        )
    assert "Required skill categories not met for build type" in str(exc_info.value.detail)
    
    # Test class-specific requirements
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_build(
            build_type=BuildType.PVE,
            focus=BuildFocus.DPS,
            character_class="invalid_class"
        )
    assert "Invalid character class" in str(exc_info.value.detail)
    
    # Test focus-specific requirements
    focus_constraints = {
        "dps": {
            "required_categories": {
                "damage": 3
            },
            "min_stats": {
                "critical_hit": 30,
                "attack_speed": 20
            }
        },
        "survival": {
            "required_categories": {
                "defense": 2,
                "healing": 1
            },
            "min_stats": {
                "life": 50000,
                "armor": 5000
            }
        }
    }
    
    constraints["focus_types"] = focus_constraints
    with open(mock_data_dir / "constraints.json", "w") as f:
        json.dump(constraints, f)
    
    # Add skills that meet build type requirements
    barbarian_constraints["skill_slots"]["available_skills"].extend([
        "Control Skill 1",
        "Control Skill 2"
    ])
    barbarian_constraints["skill_slots"]["max_skills"] = 6
    
    class_data["base_skills.json"]["skills"].update({
        "Control Skill 1": {
            "name": "Control Skill 1",
            "base_type": "control",
            "second_base_type": None,
            "categories": ["control", "aoe"],
            "cooldown": 10,
            "slot": "secondary"
        },
        "Control Skill 2": {
            "name": "Control Skill 2",
            "base_type": "control",
            "second_base_type": None,
            "categories": ["control", "aoe"],
            "cooldown": 10,
            "slot": "secondary"
        }
    })
    
    # Update class data
    with open(class_dir / "constraints.json", "w") as f:
        json.dump(barbarian_constraints, f)
    with open(class_dir / "base_skills.json", "w") as f:
        json.dump(class_data["base_skills.json"], f)
        
    # Reinitialize service with updated data
    service = BuildService(data_dir=mock_data_dir)
    
    # Now test focus requirements
    with pytest.raises(HTTPException) as exc_info:
        await service.generate_build(
            build_type=BuildType.PVE,
            focus=BuildFocus.DPS,
            character_class="barbarian"
        )
    assert "Required stats not met for build focus" in str(exc_info.value.detail)


def test_calculate_equipment_score(build_service: BuildService):
    """Test calculating equipment score."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="cleave", rank=1, essence=None)
    ]

    # Test scoring a piece
    score = build_service._calculate_equipment_score(
        equipment_name="test_helm",
        slot="head",
        data={
            "name": "Test Helm",
            "slot": "head",
            "set": "test_set",
            "stats": ["critical_hit_chance+2"]
        },
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills
    )
    assert score > 0


def test_calculate_set_score(build_service: BuildService):
    """Test calculating set score."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="cleave", rank=1, essence=None)
    ]

    # Test scoring a set
    score = build_service._calculate_set_score(
        set_name="test_set",
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills
    )
    assert score > 0
