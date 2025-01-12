"""Pydantic models for game constraints."""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict


class ConstraintValue(BaseModel):
    """Constraint value model."""
    
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    required: Optional[bool] = Field(None, description="Whether the value is required")
    unique: Optional[bool] = Field(None, description="Whether values must be unique")
    allowed_values: Optional[List[str]] = Field(None, description="List of allowed values")
    description: Optional[str] = Field(None, description="Description of the constraint")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "min_value": 0.0,
                "max_value": 100.0,
                "required": True,
                "unique": True,
                "allowed_values": ["value1", "value2"],
                "description": "Constraint description"
            }]
        }
    )


class SlotConstraints(BaseModel):
    """Slot constraints for game elements."""
    total_required: int = Field(description="Total number of slots required")
    slots: Union[Dict[str, int], List[str]] = Field(description="Slot requirements by type or list of slot names")
    valid_combinations: Optional[List[List[int]]] = Field(None, description="Valid slot combinations")


class PrimarySlotConstraints(BaseModel):
    """Primary slot constraints."""
    required: int = Field(description="Number of primary slots required")
    unique: bool = Field(description="Whether primary slots must be unique")
    star_ratings: List[int] = Field(description="Allowed star ratings")


class AuxiliarySlotConstraints(BaseModel):
    """Auxiliary slot constraints."""
    required: int = Field(description="Number of auxiliary slots required")
    must_match_primary_stars: bool = Field(description="Whether auxiliary slots must match primary star ratings")
    unique: bool = Field(description="Whether auxiliary slots must be unique")


class GemSlotConstraints(BaseModel):
    """Gem slot constraints."""
    total_required: int = Field(description="Total number of gem slots required")
    primary: PrimarySlotConstraints = Field(description="Primary gem slot constraints")
    auxiliary: AuxiliarySlotConstraints = Field(description="Auxiliary gem slot constraints")


class GameConstraints(BaseModel):
    """Game constraints model."""
    
    gem_slots: Dict[str, Any] = Field(description="Gem slot constraints")
    essence_slots: Dict[str, Any] = Field(description="Essence slot constraints")
    set_slots: Dict[str, Any] = Field(description="Set slot constraints")
    skill_slots: Dict[str, Any] = Field(description="Skill slot constraints")
    weapon_slots: Dict[str, Any] = Field(description="Weapon slot constraints")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "gem_slots": {
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
                "essence_slots": {
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
                "set_slots": {
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
                "skill_slots": {
                    "total_required": 4,
                    "slots": ["skill1", "skill2", "skill3", "skill4"]
                },
                "weapon_slots": {
                    "total_required": 4,
                    "slots": {
                        "Main Hand (Set 1)": 1,
                        "Off-Hand (Set 1)": 1,
                        "Main Hand (Set 2)": 1,
                        "Off-Hand (Set 2)": 1
                    }
                }
            }]
        }
    )
