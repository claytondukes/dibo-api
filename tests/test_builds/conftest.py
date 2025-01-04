"""Shared test fixtures and configuration."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def base_test_data(tmp_path: Path) -> dict:
    """Create base test data structure used across tests.
    
    Returns:
        dict: Dictionary containing the base test data structures
    """
    return {
        "base_skills": {
            "registry": {
                "Cleave": {
                    "base_type": "damage",
                    "second_base_type": None,
                    "base_cooldown": "6",
                    "description": "Test skill description"
                },
                "Ground_Stomp": {
                    "base_type": "control",
                    "second_base_type": None,
                    "base_cooldown": "9",
                    "description": "Test skill description"
                },
                "Leap": {
                    "base_type": "dash",
                    "second_base_type": None,
                    "base_cooldown": "12",
                    "description": "Test skill description"
                },
                "Frenzy": {
                    "base_type": "weapon",
                    "second_base_type": None,
                    "base_cooldown": "0",
                    "description": "Test weapon skill"
                }
            }
        },
        "stats": {
            "critical_hit_chance": {
                "gems": [
                    {
                        "name": "Berserker's Eye",
                        "stars": "1",
                        "base_values": [],
                        "rank_10_values": [
                            {
                                "conditions": [],
                                "value": 2.0,
                                "unit": "percentage",
                                "scaling": False
                            }
                        ]
                    }
                ],
                "essences": []
            },
            "damage_increase": {
                "gems": [],
                "essences": []
            },
            "attack_speed": {
                "gems": [],
                "essences": []
            },
            "movement_speed": {
                "gems": [],
                "essences": []
            }
        },
        "synergies": {
            "critical_hit": {
                "gems": ["Berserker's Eye"],
                "essences": [],
                "skills": []
            },
            "damage_boost": {
                "gems": ["Berserker's Eye"],
                "essences": [],
                "skills": ["Cleave"]
            },
            "control_boost": {
                "gems": [],
                "essences": [],
                "skills": ["Ground_Stomp"]
            }
        },
        "constraints": {
            "skill_types": {
                "damage": {"min": 1, "max": 3},
                "control": {"min": 1, "max": 2}
            },
            "gem_slots": {
                "total_required": 8,
                "primary": {
                    "required": 8,
                    "unique": True,
                    "star_ratings": [1, 2, 5]
                },
                "auxiliary": {
                    "required": 0,
                    "must_match_primary_stars": True,
                    "unique": True
                }
            },
            "essence_slots": {
                "total_required": 8,
                "slots": {}
            }
        },
        "gem_data": {
            "progression": {
                "Berserker's Eye": {
                    "stars": "1",
                    "ranks": {
                        "1": {
                            "effects": [
                                {
                                    "type": "stat_effect",
                                    "text": "Increases all damage you deal by 5",
                                    "conditions": []
                                }
                            ]
                        }
                    }
                }
            },
            "stat_boosts": {},
            "synergies": {},
            "gems": {}
        },
        "equipment_data": {
            "sets": {}
        },
        "class_data": {
            "essences": {
                "metadata": {
                    "version": "1.0.0",
                    "last_updated": "2025-01-04",
                    "class": "Barbarian",
                    "total_essences": 2,
                    "skills": {
                        "Cleave": {
                            "description": "Test skill",
                            "essence_count": 1
                        },
                        "Ground_Stomp": {
                            "description": "Test skill",
                            "essence_count": 1
                        }
                    }
                },
                "essences": {
                    "test_essence_1": {
                        "essence_name": "Test Essence 1",
                        "gear_slot": "Helm",
                        "modifies_skill": "Cleave",
                        "effect": "Test effect"
                    },
                    "test_essence_2": {
                        "essence_name": "Test Essence 2",
                        "gear_slot": "Chest",
                        "modifies_skill": "Ground_Stomp",
                        "effect": "Test effect"
                    }
                },
                "indexes": {
                    "by_slot": {
                        "Helm": ["test_essence_1"],
                        "Chest": ["test_essence_2"]
                    },
                    "by_skill": {
                        "Cleave": ["test_essence_1"],
                        "Ground_Stomp": ["test_essence_2"]
                    }
                }
            },
            "constraints": {
                "max_skills": 4,
                "required_types": {
                    "damage": 1,
                    "control": 1
                },
                "skill_slots": {
                    "available_skills": [
                        "Cleave",
                        "Ground_Stomp",
                        "Leap"
                    ]
                },
                "weapon_slots": {
                    "available_weapons": [
                        "Frenzy"
                    ]
                }
            }
        }
    }


@pytest.fixture
def test_data_dir(tmp_path: Path, base_test_data: dict) -> Path:
    """Create test data directory with minimal required data.
    
    Args:
        tmp_path: Pytest fixture providing temporary directory
        base_test_data: Base test data structure
        
    Returns:
        Path: Path to the indexed data directory
    """
    # Create data/indexed directory structure
    indexed_dir = tmp_path / "data" / "indexed"
    indexed_dir.mkdir(parents=True)
    
    # Define file mapping
    files_to_create = {
        "stats.json": base_test_data["stats"],
        "synergies.json": base_test_data["synergies"],
        "constraints.json": base_test_data["constraints"],
        "gems/progression.json": base_test_data["gem_data"]["progression"],
        "gems/stat_boosts.json": base_test_data["gem_data"]["stat_boosts"],
        "gems/synergies.json": base_test_data["gem_data"]["synergies"],
        "gems/gems.json": base_test_data["gem_data"]["gems"],
        "equipment/sets.json": base_test_data["equipment_data"]["sets"],
        "classes/barbarian/base_skills.json": base_test_data["base_skills"],
        "classes/barbarian/essences.json": base_test_data["class_data"]["essences"],
        "classes/barbarian/constraints.json": base_test_data["class_data"]["constraints"]
    }
    
    # Write all files
    for filename, content in files_to_create.items():
        file_path = indexed_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(content))
    
    return indexed_dir
