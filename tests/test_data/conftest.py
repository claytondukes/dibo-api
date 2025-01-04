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
def mock_data_service(
    mock_gems_data,
    mock_sets_data,
    mock_skills_data,
    tmp_path
):
    """Mock DataService fixture."""
    # Create mock data files
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)

    # Create gems data
    gems_dir = data_dir / "gems"
    gems_dir.mkdir()
    with open(gems_dir / "gems.json", "w") as f:
        json.dump(mock_gems_data, f)

    # Create sets data
    sets_dir = data_dir / "equipment"
    sets_dir.mkdir()
    with open(sets_dir / "sets.json", "w") as f:
        json.dump(mock_sets_data, f)

    # Create skills data
    classes_dir = data_dir / "classes"
    classes_dir.mkdir()
    barb_dir = classes_dir / "barbarian"
    barb_dir.mkdir()
    with open(barb_dir / "base_skills.json", "w") as f:
        json.dump(mock_skills_data["barbarian"], f)

    # Create and return service instance
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
