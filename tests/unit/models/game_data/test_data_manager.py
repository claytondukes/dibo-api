"""Tests for the game data manager."""
from pathlib import Path
from typing import Final

import pytest
from pydantic import ValidationError

from api.models.game_data.data_manager import GameDataManager
from api.models.game_data.schemas.gear import PrimaryGearSlot


@pytest.fixture
def data_manager() -> GameDataManager:
    """Create a GameDataManager instance for testing."""
    base_path = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed")
    return GameDataManager(base_path=base_path)


def test_load_equipment_sets(data_manager: GameDataManager) -> None:
    """Test loading equipment sets from JSON."""
    sets = data_manager.get_equipment_sets()
    
    # Test specific set from the real data
    flagellant = sets["Grace of the Flagellant"]
    assert flagellant.pieces == 6
    assert "DoT" in flagellant.description
    assert len(flagellant.bonuses) == 3
    assert "damage" in flagellant.bonuses["2"].lower()


def test_load_class_essences(data_manager: GameDataManager) -> None:
    """Test loading class-specific essences from JSON."""
    essences = data_manager.get_class_essences("barbarian")
    
    # Test specific essence from the real data
    flesh_of_steel = essences["flesh_of_steel"]
    assert flesh_of_steel.essence_name == "Flesh of Steel"
    assert flesh_of_steel.gear_slot == "Chest"
    assert flesh_of_steel.modifies_skill == "Iron Skin"
    assert "damage reduction" in flesh_of_steel.effect.lower()


def test_filter_essences_by_slot(data_manager: GameDataManager) -> None:
    """Test filtering essences by gear slot."""
    helm_essences = data_manager.get_class_essences("barbarian", slot="Helm")
    
    # All returned essences should be for helm slot
    assert all(essence.gear_slot == "Helm" for essence in helm_essences.values())
    
    # Should include specific helm essences from the real data
    assert "visage_of_the_living_ancients" in helm_essences
    assert "hunters_sight" in helm_essences


def test_filter_essences_by_skill(data_manager: GameDataManager) -> None:
    """Test filtering essences by skill."""
    whirlwind_essences = data_manager.get_class_essences(
        "barbarian", 
        skill="Whirlwind"
    )
    
    # All returned essences should modify Whirlwind
    assert all(
        essence.modifies_skill == "Whirlwind" 
        for essence in whirlwind_essences.values()
    )
    
    # Should include specific Whirlwind essences from the real data
    assert "five_fresh_claws" in whirlwind_essences


def test_invalid_class_name(data_manager: GameDataManager) -> None:
    """Test that invalid class names raise an error."""
    with pytest.raises(ValueError, match="Invalid class name: invalid_class"):
        data_manager.get_class_essences("invalid_class")
