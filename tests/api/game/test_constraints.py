"""Tests for constraint schema models."""

from api.models.game_data.schemas.constraints import (
    ConstraintValue,
    SlotConstraints,
    PrimarySlotConstraints,
    AuxiliarySlotConstraints,
    GameConstraints
)


def test_constraint_value():
    """Test ConstraintValue model."""
    constraint = ConstraintValue(
        min_value=0.0,
        max_value=100.0,
        required=True,
        unique=True,
        allowed_values=["value1", "value2"],
        description="Test constraint"
    )
    
    assert constraint.min_value == 0.0
    assert constraint.max_value == 100.0
    assert constraint.required is True
    assert constraint.unique is True
    assert constraint.allowed_values == ["value1", "value2"]
    assert constraint.description == "Test constraint"
    
    # Test optional fields
    constraint = ConstraintValue()
    assert constraint.min_value is None
    assert constraint.max_value is None
    assert constraint.required is None
    assert constraint.unique is None
    assert constraint.allowed_values is None
    assert constraint.description is None


def test_slot_constraints():
    """Test SlotConstraints model."""
    # Test with dict slots
    constraints = SlotConstraints(
        total_required=8,
        slots={"Head": 1, "Chest": 1},
        valid_combinations=[[2]]
    )
    
    assert constraints.total_required == 8
    assert constraints.slots == {"Head": 1, "Chest": 1}
    assert constraints.valid_combinations == [[2]]
    
    # Test with list slots
    constraints = SlotConstraints(
        total_required=4,
        slots=["slot1", "slot2", "slot3", "slot4"]
    )
    assert constraints.total_required == 4
    assert constraints.slots == ["slot1", "slot2", "slot3", "slot4"]
    assert constraints.valid_combinations is None


def test_primary_slot_constraints():
    """Test PrimarySlotConstraints model."""
    constraints = PrimarySlotConstraints(
        required=8,
        unique=True,
        star_ratings=[1, 2, 5]
    )
    
    assert constraints.required == 8
    assert constraints.unique is True
    assert constraints.star_ratings == [1, 2, 5]


def test_auxiliary_slot_constraints():
    """Test AuxiliarySlotConstraints model."""
    constraints = AuxiliarySlotConstraints(
        required=0,
        must_match_primary_stars=True,
        unique=True
    )
    
    assert constraints.required == 0
    assert constraints.must_match_primary_stars is True
    assert constraints.unique is True


def test_game_constraints():
    """Test GameConstraints model."""
    constraints = GameConstraints(
        gem_slots={
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
        essence_slots={
            "total_required": 8,
            "slots": {
                "Head": 1,
                "Shoulders": 1,
                "Chest": 1,
                "Legs": 1,
                "Main Hand (Set 1)": 1,
                "Off-Hand (Set 1)": 1,
                "Main Hand (Set 2)": 1,
                "Off-Hand (Set 2)": 1
            }
        },
        set_slots={
            "total_required": 8,
            "slots": {
                "Ring": 2,
                "Neck": 1,
                "Hands": 1,
                "Waist": 1,
                "Feet": 1,
                "Bracer": 2
            },
            "valid_combinations": [
                [6, 2],
                [4, 4],
                [4, 2, 2],
                [2, 2, 2, 2]
            ]
        },
        skill_slots={
            "total_required": 4,
            "slots": ["skill1", "skill2", "skill3", "skill4"]
        },
        weapon_slots={
            "total_required": 4,
            "slots": {
                "Main Hand (Set 1)": 1,
                "Off-Hand (Set 1)": 1,
                "Main Hand (Set 2)": 1,
                "Off-Hand (Set 2)": 1
            }
        }
    )
    
    assert isinstance(constraints.gem_slots, dict)
    assert isinstance(constraints.essence_slots, dict)
    assert isinstance(constraints.set_slots, dict)
    assert isinstance(constraints.skill_slots, dict)
    assert isinstance(constraints.weapon_slots, dict)
    
    assert constraints.gem_slots["total_required"] == 8
    assert constraints.essence_slots["total_required"] == 8
    assert constraints.set_slots["total_required"] == 8
    assert constraints.skill_slots["total_required"] == 4
    assert constraints.weapon_slots["total_required"] == 4
