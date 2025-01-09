"""Unit tests for gear schema models."""
from typing import Final

import pytest
from pydantic import ValidationError

from api.models.game_data.schemas.gear import GearSlot, SetBonus


def test_gear_slot_primary_values() -> None:
    """Test that GearSlot enum contains all required primary gear slots."""
    expected_slots: Final[set[str]] = {
        "HEAD",
        "SHOULDERS",
        "CHEST",
        "LEGS",
        "MAIN_HAND_1",  # Primary weapon
        "OFF_HAND_1",   # Primary shield/off-hand
        "MAIN_HAND_2",  # Secondary weapon
        "OFF_HAND_2",   # Secondary shield/off-hand
    }
    
    actual_slots: set[str] = {
        slot.name for slot in GearSlot 
        if slot.value in {
            "head", "chest", "shoulders", "legs",
            "main_hand_1", "off_hand_1",
            "main_hand_2", "off_hand_2"
        }
    }
    assert actual_slots == expected_slots, \
        f"GearSlot enum missing required primary slots. Expected {expected_slots}, got {actual_slots}"


def test_gear_slot_set_values() -> None:
    """Test that GearSlot enum contains all required set gear slots."""
    expected_slots: Final[set[str]] = {
        "NECK",
        "WAIST",
        "HANDS",
        "FEET",
        "RING_1",
        "RING_2",
        "BRACER_1",
        "BRACER_2"
    }
    
    actual_slots: set[str] = {
        slot.name for slot in GearSlot 
        if slot.value in {
            "neck", "waist", "hands", "feet",
            "ring_1", "ring_2",
            "bracer_1", "bracer_2"
        }
    }
    assert actual_slots == expected_slots, \
        f"GearSlot enum missing required set slots. Expected {expected_slots}, got {actual_slots}"


def test_gear_slot_invalid_value() -> None:
    """Test that invalid gear slot values raise ValueError."""
    with pytest.raises(ValueError):
        GearSlot("invalid_slot")


def test_set_bonus_valid() -> None:
    """Test creation of a valid set bonus."""
    bonus = SetBonus(
        pieces=4,
        description="A powerful set focused on critical hits",
        bonuses={
            "2": "+10% Critical Hit Chance",
            "4": "+50% Critical Hit Damage"
        },
        use_case="Best for crit-focused builds"
    )
    assert bonus.pieces == 4
    assert len(bonus.bonuses) == 2
    assert bonus.use_case == "Best for crit-focused builds"


def test_set_bonus_missing_field() -> None:
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        SetBonus(
            pieces=4,
            description="A powerful set",
            # Missing bonuses field
            use_case="Best for crit builds"
        )
