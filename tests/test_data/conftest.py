"""Test fixtures for game data tests."""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.data.models import BuildCategory, GemBase, EquipmentSet, Skill
from api.data.service import DataService, get_data_service


@pytest.fixture
def mock_gems_data():
    """Mock gems test data."""
    return {
        "gems_by_skill": {
            BuildCategory.MOVEMENT.value: [
                {
                    "Name": "Freedom and Devotion",
                    "Stars": "2",
                    "Base Effect": "Increases Movement Speed by 10%",
                    "Rank 10 Effect": "Increases Movement Speed by 20%"
                }
            ],
            BuildCategory.ATTACK.value: [
                {
                    "Name": "Lightning Core",
                    "Stars": "5",
                    "Base Effect": "Lightning strikes enemies",
                    "Rank 10 Effect": "Lightning strikes more frequently"
                }
            ]
        }
    }


@pytest.fixture
def mock_sets_data():
    """Mock equipment sets test data."""
    return {
        "registry": {
            "Grace of the Flagellant": {
                "pieces": 6,
                "description": "A powerful set for damage dealers",
                "bonuses": {
                    "2": "+15% damage",
                    "4": "+30% damage",
                    "6": "+50% damage"
                },
                "use_case": "Best for high damage builds"
            },
            "Shepherd's Call to Wolves": {
                "pieces": 4,
                "description": "A set for summoners",
                "bonuses": {
                    "2": "+10% summon damage",
                    "4": "+25% summon damage"
                },
                "use_case": "Best for summoner builds"
            }
        }
    }


@pytest.fixture
def mock_skills_data():
    """Mock skills test data."""
    return {
        "barbarian": {
            "skills": [
                {
                    "name": "Whirlwind",
                    "description": "Spin to win",
                    "cooldown": 8.0,
                    "categories": [
                        BuildCategory.ATTACK.value,
                        BuildCategory.CHANNELED.value
                    ]
                },
                {
                    "name": "Sprint",
                    "description": "Run faster",
                    "cooldown": 12.0,
                    "categories": [BuildCategory.MOVEMENT.value]
                }
            ]
        }
    }


@pytest.fixture
def mock_stats_data():
    """Mock stats data."""
    return {
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
                    "name": "Ruby",
                    "stars": "2",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 5.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ],
            "essences": [
                {
                    "name": "Lightning Core",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 15.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ]
        },
        "attack_speed": {
            "gems": [
                {
                    "name": "Swift Stone",
                    "stars": "3",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 3.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ],
            "essences": []
        },
        "movement_speed": {
            "gems": [
                {
                    "name": "Fleet Foot",
                    "stars": "2",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 4.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ],
            "essences": []
        },
        "life": {
            "gems": [
                {
                    "name": "Ruby of Vitality",
                    "stars": "3",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 10.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ],
            "essences": [
                {
                    "name": "Life Core",
                    "base_values": [
                        {
                            "conditions": [],
                            "value": 20.0,
                            "unit": "percentage",
                            "scaling": False
                        }
                    ],
                    "rank_10_values": [],
                    "conditions": [],
                    "rank_10_conditions": []
                }
            ]
        }
    }


@pytest.fixture
def mock_data_service(
    mock_gems_data,
    mock_sets_data,
    mock_skills_data,
    mock_stats_data,
    tmp_path
):
    """Mock DataService fixture."""
    # Create data directory structure
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)
    
    # Create gems directory and files
    gems_dir = data_dir / "gems"
    gems_dir.mkdir()
    with open(gems_dir / "gems.json", "w") as f:
        json.dump(mock_gems_data, f)
        
    # Create equipment directory and files
    equipment_dir = data_dir / "equipment"
    equipment_dir.mkdir()
    with open(equipment_dir / "sets.json", "w") as f:
        json.dump(mock_sets_data, f)
        
    # Create classes directory and files
    classes_dir = data_dir / "classes"
    classes_dir.mkdir()
    barb_dir = classes_dir / "barbarian"
    barb_dir.mkdir()
    with open(barb_dir / "base_skills.json", "w") as f:
        json.dump(mock_skills_data["barbarian"], f)

    # Create stats file
    with open(data_dir / "stats.json", "w") as f:
        json.dump(mock_stats_data, f)
    
    return DataService(data_dir=data_dir)


@pytest.fixture
def test_app(mock_data_service):
    """Test app fixture with mocked data service."""
    from api.main import app

    app.dependency_overrides[get_data_service] = lambda: mock_data_service
    return app


@pytest.fixture
def test_client(test_app):
    """Test client fixture."""
    with TestClient(test_app) as client:
        yield client
