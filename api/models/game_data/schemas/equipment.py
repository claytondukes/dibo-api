"""
Pydantic models for equipment-related data structures.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EquipmentSlot(str, Enum):
    """Valid equipment slot types."""
    
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    GLOVES = "gloves"
    BOOTS = "boots"
    ACCESSORY = "accessory"


class SetMetadata(BaseModel):
    """Metadata for equipment sets."""
    
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


class EquipmentSet(BaseModel):
    """Individual equipment set details."""
    
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


class EquipmentSets(BaseModel):
    """Collection of equipment sets."""
    
    metadata: SetMetadata = Field(
        ...,
        description="Global metadata for equipment sets"
    )
    registry: Dict[str, EquipmentSet] = Field(
        ...,
        description="Registry of all equipment sets, keyed by set name"
    )
