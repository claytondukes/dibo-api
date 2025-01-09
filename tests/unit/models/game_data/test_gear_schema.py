"""Unit tests for gear schema models."""
from typing import Final

import pytest
from pydantic import ValidationError

from api.models.game_data.schemas.gear import (
    PrimaryGearSlot,
    SetGearSlot,
    EssenceSlot,
    PrimaryGearItem,
    SetGearItem
)


def test_primary_gear_slot_enum_values() -> None:
    """Test that PrimaryGearSlot enum contains all required gear slots."""
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
    
    actual_slots: set[str] = {slot.name for slot in PrimaryGearSlot}
    assert actual_slots == expected_slots, \
        f"PrimaryGearSlot enum missing required slots. Expected {expected_slots}, got {actual_slots}"


def test_set_gear_slot_enum_values() -> None:
    """Test that SetGearSlot enum contains all required gear slots."""
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
    
    actual_slots: set[str] = {slot.name for slot in SetGearSlot}
    assert actual_slots == expected_slots, \
        f"SetGearSlot enum missing required slots. Expected {expected_slots}, got {actual_slots}"


def test_primary_gear_slot_invalid_value() -> None:
    """Test that invalid primary gear slot values raise ValueError."""
    with pytest.raises(ValueError, match="'INVALID_SLOT' is not a valid PrimaryGearSlot"):
        PrimaryGearSlot("INVALID_SLOT")


def test_set_gear_slot_invalid_value() -> None:
    """Test that invalid set gear slot values raise ValueError."""
    with pytest.raises(ValueError, match="'INVALID_SLOT' is not a valid SetGearSlot"):
        SetGearSlot("INVALID_SLOT")


def test_essence_slot_empty() -> None:
    """Test creation of an empty essence slot."""
    slot = EssenceSlot()
    assert slot.available is True
    assert slot.current_essence is None


def test_essence_slot_with_essence() -> None:
    """Test creation of an essence slot with an essence."""
    slot = EssenceSlot(current_essence="Test Essence")
    assert slot.available is True
    assert slot.current_essence == "Test Essence"


def test_essence_slot_unavailable() -> None:
    """Test creation of an unavailable essence slot."""
    slot = EssenceSlot(available=False)
    assert slot.available is False
    assert slot.current_essence is None


def test_essence_slot_unavailable_with_essence() -> None:
    """Test that unavailable slots cannot have essences."""
    with pytest.raises(ValueError, match="Unavailable slots cannot have essences"):
        EssenceSlot(available=False, current_essence="Test Essence")


def test_primary_gear_item_valid() -> None:
    """Test creation of a valid primary gear item."""
    item = PrimaryGearItem(
        name="Test Item",
        slot=PrimaryGearSlot.HEAD,
        attributes={
            "strength": "100",
            "fortitude": "150"
        },
        essence_slots=[
            EssenceSlot(current_essence="Test Essence"),
            EssenceSlot()
        ]
    )
    assert item.name == "Test Item"
    assert item.slot == PrimaryGearSlot.HEAD
    assert len(item.essence_slots) == 2
    assert item.essence_slots[0].current_essence == "Test Essence"


def test_set_gear_item_valid() -> None:
    """Test creation of a valid set gear item."""
    item = SetGearItem(
        name="Test Set Item",
        slot=SetGearSlot.NECK,
        set_name="Test Set",
        attributes={
            "strength": "100",
            "fortitude": "150"
        }
    )
    assert item.name == "Test Set Item"
    assert item.slot == SetGearSlot.NECK
    assert item.set_name == "Test Set"


def test_primary_gear_item_minimal() -> None:
    """Test creation of a primary gear item with minimal attributes."""
    item = PrimaryGearItem(
        name="Test Item",
        slot=PrimaryGearSlot.HEAD,
        attributes={},
        essence_slots=[]
    )
    assert item.name == "Test Item"
    assert item.slot == PrimaryGearSlot.HEAD
    assert len(item.essence_slots) == 0


def test_set_gear_item_minimal() -> None:
    """Test creation of a set gear item with minimal attributes."""
    item = SetGearItem(
        name="Test Set Item",
        slot=SetGearSlot.NECK,
        set_name="Test Set",
        attributes={}
    )
    assert item.name == "Test Set Item"
    assert item.slot == SetGearSlot.NECK
    assert item.set_name == "Test Set"


def test_primary_gear_item_invalid_empty_name() -> None:
    """Test that primary gear items must have a non-empty name."""
    with pytest.raises(ValidationError, match="String should have at least 1 characters"):
        PrimaryGearItem(
            name="",
            slot=PrimaryGearSlot.HEAD,
            attributes={},
            essence_slots=[]
        )


def test_set_gear_item_invalid_empty_name() -> None:
    """Test that set gear items must have a non-empty name."""
    with pytest.raises(ValidationError, match="String should have at least 1 characters"):
        SetGearItem(
            name="",
            slot=SetGearSlot.NECK,
            set_name="Test Set",
            attributes={}
        )
