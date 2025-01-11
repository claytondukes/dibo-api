"""
Pydantic models for set bonus data structures.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GearSlot(str, Enum):
    """Valid gear slot types based on character equipment layout."""
    
    # Right side slots (normal gear)
    HEAD = "Head"           # Helm slot
    CHEST = "Chest"        # Torso armor
    SHOULDERS = "Shoulders" # Shoulder armor 
    LEGS = "Legs"          # Leg armor
    MAIN_HAND_1 = "Main Hand (Set 1)"  # Primary weapon set 1
    OFF_HAND_1 = "Off-Hand (Set 1)"    # Off-hand weapon/shield set 1
    MAIN_HAND_2 = "Main Hand (Set 2)"  # Primary weapon set 2
    OFF_HAND_2 = "Off-Hand (Set 2)"    # Off-hand weapon/shield set 2


class SetSlot(str, Enum):
    """Valid set item slots (left side)."""
    
    HEAD = "Head"           # Head piece
    SHOULDERS = "Shoulders" # Shoulders piece
    CHEST = "Chest"        # Chest piece
    LEGS = "Legs"          # Legs piece
    HANDS = "Hands"        # Gloves
    FEET = "Feet"          # Boots
    WAIST = "Waist"        # Belt
    RING_1 = "Ring 1"      # First ring slot
    RING_2 = "Ring 2"      # Second ring slot
    NECK = "Neck"          # Necklace
    BRACER_1 = "Bracer 1"  # First bracer slot
    BRACER_2 = "Bracer 2"  # Second bracer slot


class SetMetadata(BaseModel):
    """Metadata for set bonuses."""
    
    bonus_thresholds: List[int] = Field(
        ...,
        description="Piece counts that activate set bonuses (e.g., [2, 4, 6])"
    )
    bonus_rules: str = Field(
        ...,
        description="Rules for how set bonuses are applied"
    )


class SetBonuses(BaseModel):
    """Bonuses for different piece counts of a set."""
    
    two: str = Field(..., alias="2", description="2-piece set bonus")
    four: Optional[str] = Field(None, alias="4", description="4-piece set bonus")
    six: Optional[str] = Field(None, alias="6", description="6-piece set bonus")


class SetBonus(BaseModel):
    """Individual set bonus details."""
    
    pieces: int = Field(
        ...,
        description="Total number of pieces in the set"
    )
    description: str = Field(
        ...,
        description="Description of the set's theme or focus"
    )
    bonuses: SetBonuses = Field(
        ...,
        description="Bonuses granted at different piece counts"
    )
    use_case: Optional[str] = Field(
        None,
        description="Recommended use cases for the set"
    )


class SetBonusRegistry(BaseModel):
    """Collection of all set bonuses."""
    
    metadata: SetMetadata = Field(
        ...,
        description="Global metadata for set bonuses"
    )
    registry: Dict[str, SetBonus] = Field(
        ...,
        description="Registry of all set bonuses, keyed by set name"
    )
