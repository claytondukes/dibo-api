"""Integration tests for gear-related endpoints."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.main import create_app
from api.models.game_data.data_manager import GameDataManager


@pytest.fixture
def client(data_manager: GameDataManager) -> TestClient:
    """Create a test client."""
    app = create_app()
    app.state.data_manager = data_manager
    return TestClient(app)


@pytest.fixture
def sample_gear_data(tmp_path: Path) -> Path:
    """Create sample gear data for testing."""
    equipment_dir = tmp_path / "equipment"
    equipment_dir.mkdir(parents=True)
    
    gear_data = {
        "barbarian": {
            "mighty_axe": {
                "name": "Mighty Axe",
                "slot": "main_hand_1",
                "stats": {"strength": "100", "damage": "150-200"}
            },
            "plate_helm": {
                "name": "Plate Helm",
                "slot": "head",
                "stats": {"fortitude": "80", "armor": "120"}
            }
        },
        "wizard": {
            "crystal_staff": {
                "name": "Crystal Staff",
                "slot": "main_hand_1",
                "stats": {"willpower": "120", "damage": "100-150"}
            }
        }
    }
    
    gear_path = equipment_dir / "gear.json"
    with open(gear_path, "w") as f:
        json.dump(gear_data, f)
    
    return tmp_path


@pytest.mark.parametrize(
    "query_params,expected_items,expected_total",
    [
        # Test no filters
        ({}, 3, 3),
        # Test class filter
        ({"class": "barbarian"}, 2, 2),
        # Test slot filter
        ({"slot": "main_hand_1"}, 2, 2),
        # Test combined filters
        ({"class": "wizard", "slot": "main_hand_1"}, 1, 1),
        # Test pagination
        ({"per_page": 1, "page": 2}, 1, 3),
    ]
)
def test_list_gear(
    client: TestClient,
    sample_gear_data: Path,
    query_params: dict,
    expected_items: int,
    expected_total: int
) -> None:
    """Test listing gear items with various filters."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/game/gear",
        params=query_params
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) == expected_items
    assert data["total"] == expected_total
    
    # Verify response structure
    assert all(
        isinstance(item["name"], str) and
        isinstance(item["slot"], str) and
        isinstance(item["stats"], dict)
        for item in data["items"]
    )
