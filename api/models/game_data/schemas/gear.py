"""Schema definitions for gear-related models."""
from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel, Field, model_validator


class PrimaryGearSlot(str, Enum):
    """Primary gear slots that can hold essences."""
    
    HEAD = "head"
    SHOULDERS = "shoulders"
    CHEST = "chest"
    LEGS = "legs"
    MAIN_HAND_1 = "main_hand_1"  # Primary weapon
    OFF_HAND_1 = "off_hand_1"    # Primary shield/off-hand
    MAIN_HAND_2 = "main_hand_2"  # Secondary weapon
    OFF_HAND_2 = "off_hand_2"    # Secondary shield/off-hand


class SetGearSlot(str, Enum):
    """Set item slots for legendary sets."""
    
    NECK = "neck"
    WAIST = "waist"
    HANDS = "hands"
    FEET = "feet"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    BRACER_1 = "bracer_1"
    BRACER_2 = "bracer_2"


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


class PrimaryGearItem(BaseModel):
    """A piece of primary gear that can hold essences."""
    
    name: str = Field(min_length=1, description="Name of the gear item")
    slot: PrimaryGearSlot = Field(description="The slot this item can be equipped in")
    essence_slot: EssenceSlot = Field(default_factory=EssenceSlot, description="Essence modification slot")
    attributes: dict[str, str] = Field(
        description="Item attributes (e.g., strength, fortitude, damage)"
    )


class SetGearItem(BaseModel):
    """A piece of set gear that contributes to set bonuses."""
    
    name: str = Field(min_length=1, description="Name of the gear item")
    slot: SetGearSlot = Field(description="The slot this item can be equipped in")
    set_name: str = Field(description="The set this item belongs to")
    attributes: dict[str, str] = Field(
        description="Item attributes (e.g., strength, fortitude, damage)"
    )
