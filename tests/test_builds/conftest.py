"""Shared test fixtures and configuration."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing."""
    return "test_token"


@pytest.fixture
def base_test_data(tmp_path: Path) -> dict:
    """Create base test data structure used across tests.
    
    Returns:
        dict: Dictionary containing the base test data structures
    """
    return {
        "metadata": {
            "version": "1.0",
            "last_updated": "2025-01-04",
            "total_count": 4
        },
        "stats": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04"
            },
            "stats": {
                "critical_hit_chance": {
                    "base": 5.0,
                    "max": 100.0
                }
            }
        },
        "synergies": {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04"
            },
            "synergies": {
                "critical_hit": {
                    "gems": ["test_gem"],
                    "essences": ["test_essence"],
                    "skills": ["cleave"]
                }
            }
        },
        "constraints": {
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
        "classes": {
            "barbarian": {
                "base_skills": {
                    "metadata": {
                        "version": "1.0",
                        "last_updated": "2025-01-04"
                    },
                    "skills": {
                        "cleave": {
                            "skill_name": "Cleave",
                            "base_type": "damage",
                            "second_base_type": None,
                            "categories": ["damage", "melee"],
                            "cooldown": 6,
                            "slot": "primary"
                        }
                    }
                },
                "essences": {
                    "metadata": {
                        "version": "1.0",
                        "last_updated": "2025-01-04"
                    },
                    "essences": {
                        "test_essence": {
                            "name": "Test Essence",
                            "type": "legendary",
                            "slot": "weapon"
                        }
                    },
                    "indexes": {
                        "by_slot": {
                            "weapon": ["test_essence"]
                        }
                    }
                },
                "constraints": {
                    "gem_slots": {
                        "total_required": 8,
                        "unique": True
                    },
                    "essence_slots": {
                        "total_required": 6,
                        "unique": True
                    }
                }
            }
        },
        "equipment": {
            "sets": {
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2025-01-04"
                },
                "sets": {
                    "test_set": {
                        "name": "Test Set",
                        "pieces": ["test_helm", "test_chest"],
                        "bonuses": {
                            "2": ["critical_hit_chance+5"]
                        }
                    }
                },
                "gear": {
                    "head": {
                        "test_helm": {
                            "name": "Test Helm",
                            "slot": "head",
                            "set": "test_set",
                            "stats": ["critical_hit_chance+2"]
                        }
                    }
                }
            }
        },
        "gems": {
            "progression": {
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2025-01-04"
                },
                "progression": {
                    "test_gem": {
                        "ranks": {
                            "1": {"power": 1},
                            "10": {"power": 10}
                        }
                    }
                }
            },
            "stat_boosts": {
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2025-01-04"
                },
                "boosts": {
                    "test_gem": {
                        "critical_hit_chance": 2.0
                    }
                }
            },
            "synergies": {
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2025-01-04"
                },
                "synergies": {
                    "test_gem": {
                        "skills": ["cleave"],
                        "essences": ["test_essence"]
                    }
                }
            },
            "gems": {
                "metadata": {
                    "version": "1.0",
                    "last_updated": "2025-01-04"
                },
                "gems": {
                    "test_gem": {
                        "name": "Test Gem",
                        "type": "legendary",
                        "stats": ["critical_hit_chance"]
                    }
                }
            }
        }
    }


@pytest.fixture
def test_data_dir(tmp_path: Path, base_test_data: dict) -> Path:
    """Create test data directory with minimal required data."""
    # Create indexed directory
    indexed_dir = tmp_path / "data" / "indexed"
    indexed_dir.mkdir(parents=True)

    # Create required directories
    (indexed_dir / "classes").mkdir()
    (indexed_dir / "classes/barbarian").mkdir()
    (indexed_dir / "equipment").mkdir()
    (indexed_dir / "gems").mkdir()

    # Write core data files
    with open(indexed_dir / "synergies.json", "w") as f:
        json.dump(base_test_data["synergies"], f)
    with open(indexed_dir / "constraints.json", "w") as f:
        json.dump(base_test_data["constraints"], f)
    with open(indexed_dir / "stats.json", "w") as f:
        json.dump(base_test_data["stats"], f)

    # Write class data files
    with open(indexed_dir / "classes/barbarian/base_skills.json", "w") as f:
        json.dump(base_test_data["classes"]["barbarian"]["base_skills"], f)
    with open(indexed_dir / "classes/barbarian/essences.json", "w") as f:
        json.dump(base_test_data["classes"]["barbarian"]["essences"], f)
    with open(indexed_dir / "classes/barbarian/constraints.json", "w") as f:
        json.dump(base_test_data["classes"]["barbarian"]["constraints"], f)

    # Write equipment data files
    with open(indexed_dir / "equipment/sets.json", "w") as f:
        json.dump(base_test_data["equipment"]["sets"], f)

    # Write gem data files
    with open(indexed_dir / "gems/progression.json", "w") as f:
        json.dump(base_test_data["gems"]["progression"], f)
    with open(indexed_dir / "gems/stat_boosts.json", "w") as f:
        json.dump(base_test_data["gems"]["stat_boosts"], f)
    with open(indexed_dir / "gems/synergies.json", "w") as f:
        json.dump(base_test_data["gems"]["synergies"], f)
    with open(indexed_dir / "gems/gems.json", "w") as f:
        json.dump(base_test_data["gems"]["gems"], f)

    return indexed_dir
