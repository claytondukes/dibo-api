"""Schema definitions for gear-related models."""
from enum import Enum, auto
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class GearSlot(str, Enum):
    """Enumeration of valid primary gear slots."""
    
    HEAD = "head"
    SHOULDERS = "shoulders"
    CHEST = "chest"
    LEGS = "legs"
    MAIN_HAND_1 = "main_hand_1"  # Primary weapon
    OFF_HAND_1 = "off_hand_1"    # Primary shield/off-hand
    MAIN_HAND_2 = "main_hand_2"  # Secondary weapon
    OFF_HAND_2 = "off_hand_2"    # Secondary shield/off-hand


class GearAttributes(BaseModel):
    """Core attributes that can be present on gear items."""
    
    strength: int = Field(ge=0, description="Physical power and weapon damage")
    fortitude: int = Field(ge=0, description="Health and armor")
    willpower: int = Field(ge=0, description="Skill power and resistance")


class EssenceSlot(BaseModel):
    """A slot that can hold a skill-modifying essence."""
    
    available: bool = Field(default=True, description="Whether this slot can hold an essence")
    current_essence: Optional[str] = Field(
        default=None, 
        description="The name of the currently socketed essence, if any"
    )

    @model_validator(mode='after')
    def validate_essence_slot(self) -> 'EssenceSlot':
        """Validate that unavailable slots cannot have essences."""
        if not self.available and self.current_essence is not None:
            raise ValueError("Unavailable slots cannot have essences")
        return self


class GearItem(BaseModel):
    """A piece of primary gear that can be equipped."""
    
    name: str = Field(min_length=1, description="Name of the gear item")
    slot: GearSlot = Field(description="The slot this item can be equipped in")
    attributes: GearAttributes = Field(description="Core attributes provided by this item")
    essence_slot: EssenceSlot = Field(
        default_factory=EssenceSlot,
        description="The essence slot for this item, if any"
    )
