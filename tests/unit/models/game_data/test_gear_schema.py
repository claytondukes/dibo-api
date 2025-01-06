"""Unit tests for gear schema models."""
from typing import Final

import pytest
from pydantic import ValidationError

from api.models.game_data.schemas.gear import (
    GearSlot,
    GearAttributes,
    EssenceSlot,
    GearItem
)


def test_gear_slot_enum_values() -> None:
    """Test that GearSlot enum contains all required gear slots."""
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
    
    actual_slots: set[str] = {slot.name for slot in GearSlot}
    assert actual_slots == expected_slots, \
        f"GearSlot enum missing required slots. Expected {expected_slots}, got {actual_slots}"


def test_gear_slot_invalid_value() -> None:
    """Test that invalid gear slot values raise ValueError."""
    with pytest.raises(ValueError, match="'INVALID_SLOT' is not a valid GearSlot"):
        GearSlot("INVALID_SLOT")


def test_gear_attributes_valid() -> None:
    """Test that valid gear attributes are accepted."""
    attrs = GearAttributes(
        strength=100,
        fortitude=150,
        willpower=75
    )
    assert attrs.strength == 100
    assert attrs.fortitude == 150
    assert attrs.willpower == 75


def test_gear_attributes_invalid_negative() -> None:
    """Test that negative attribute values are rejected."""
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        GearAttributes(strength=-1, fortitude=0, willpower=0)


def test_gear_attributes_invalid_type() -> None:
    """Test that non-integer attribute values are rejected."""
    with pytest.raises(ValidationError):
        GearAttributes(strength="invalid", fortitude=0, willpower=0)  # type: ignore


def test_essence_slot_empty() -> None:
    """Test creation of an empty essence slot."""
    slot = EssenceSlot()
    assert slot.available is True
    assert slot.current_essence is None


def test_essence_slot_with_essence() -> None:
    """Test creation of an essence slot with an essence."""
    slot = EssenceSlot(current_essence="Whirlwind")
    assert slot.available is True
    assert slot.current_essence == "Whirlwind"


def test_essence_slot_unavailable() -> None:
    """Test creation of an unavailable essence slot."""
    slot = EssenceSlot(available=False)
    assert slot.available is False
    assert slot.current_essence is None


def test_essence_slot_unavailable_with_essence() -> None:
    """Test that unavailable slots cannot have essences."""
    with pytest.raises(ValidationError, match="Unavailable slots cannot have essences"):
        EssenceSlot(available=False, current_essence="Whirlwind")


def test_gear_item_valid() -> None:
    """Test creation of a valid gear item."""
    item = GearItem(
        name="Mighty Helm of the Bear",
        slot=GearSlot.HEAD,
        attributes=GearAttributes(strength=100, fortitude=150, willpower=75),
        essence_slot=EssenceSlot(available=True, current_essence="Whirlwind")
    )
    assert item.name == "Mighty Helm of the Bear"
    assert item.slot == GearSlot.HEAD
    assert item.attributes.strength == 100
    assert item.essence_slot.current_essence == "Whirlwind"


def test_gear_item_minimal() -> None:
    """Test creation of a gear item with minimal attributes."""
    item = GearItem(
        name="Basic Sword",
        slot=GearSlot.MAIN_HAND_1,
        attributes=GearAttributes(strength=0, fortitude=0, willpower=0)
    )
    assert item.name == "Basic Sword"
    assert item.slot == GearSlot.MAIN_HAND_1
    assert item.essence_slot.available is True
    assert item.essence_slot.current_essence is None


def test_gear_item_invalid_empty_name() -> None:
    """Test that gear items must have a non-empty name."""
    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        GearItem(
            name="",
            slot=GearSlot.HEAD,
            attributes=GearAttributes(strength=0, fortitude=0, willpower=0)
        )
