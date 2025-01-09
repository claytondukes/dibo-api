"""Integration tests for gear-related endpoints.

The gear system consists of two categories:
1. Normal (Primary) Gear - Core equipment slots (8 total)
   - Head, Chest, Shoulders, Legs
   - Main Hand (Set 1), Off-Hand (Set 1)
   - Main Hand (Set 2), Off-Hand (Set 2)

2. Set Items - Special gear slots (8 total)
   - Neck, Waist
   - Hands, Feet
   - Ring 1, Ring 2
   - Bracer 1, Bracer 2

Note: The gear slots are fixed and defined in the GearSlot enum.
Set bonuses are stored in /data/indexed/equipment/sets.json.
Class-specific essence effects that modify skills are stored separately.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.models.game_data.schemas.gear import GearSlot


@pytest.fixture
def client(data_manager) -> TestClient:
    """Create a test client."""
    from api.main import create_app
    app = create_app()
    app.state.data_manager = data_manager
    return TestClient(app)


@pytest.mark.parametrize(
    "query_params,expected_slots",
    [
        # Test no filters - all gear slots
        ({}, set(GearSlot)),
        # Test primary gear slots
        (
            {"type": "primary"}, 
            {
                GearSlot.HEAD, GearSlot.CHEST, GearSlot.SHOULDERS, GearSlot.LEGS,
                GearSlot.MAIN_HAND_1, GearSlot.OFF_HAND_1,
                GearSlot.MAIN_HAND_2, GearSlot.OFF_HAND_2
            }
        ),
        # Test set gear slots
        (
            {"type": "set"},
            {
                GearSlot.NECK, GearSlot.WAIST, GearSlot.HANDS, GearSlot.FEET,
                GearSlot.RING_1, GearSlot.RING_2,
                GearSlot.BRACER_1, GearSlot.BRACER_2
            }
        ),
    ]
)
def test_list_gear_slots(
    client: TestClient,
    query_params: dict,
    expected_slots: set[GearSlot]
) -> None:
    """Test listing available gear slots."""
    settings = get_settings()
    response = client.get(
        f"{settings.API_V1_STR}/game/gear/slots",
        params=query_params
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert set(data["slots"]) == {slot.value for slot in expected_slots}
