"""Pydantic models for game constraints."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ConstraintValue(BaseModel):
    """A single constraint value."""
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    allowed_values: Optional[List[str]] = Field(None, description="List of allowed values")
    description: Optional[str] = Field(None, description="Description of the constraint")


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
    """Collection of game constraints."""
    gem_slots: GemSlotConstraints = Field(description="Gem slot constraints")
    essence_slots: SlotConstraints = Field(description="Essence slot constraints")
    set_slots: SlotConstraints = Field(description="Set slot constraints")
    skill_slots: SlotConstraints = Field(description="Skill slot constraints")
    weapon_slots: SlotConstraints = Field(description="Weapon slot constraints")

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        validate_assignment = False
