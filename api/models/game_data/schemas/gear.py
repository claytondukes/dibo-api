"""Schema definitions for gear-related models."""
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class GearSlot(str, Enum):
    """Available gear slots for all classes."""
    
    # Primary gear slots
    HEAD = "head"
    SHOULDERS = "shoulders"
    CHEST = "chest"
    LEGS = "legs"
    MAIN_HAND_1 = "main_hand_1"  # Primary weapon
    OFF_HAND_1 = "off_hand_1"    # Primary shield/off-hand
    MAIN_HAND_2 = "main_hand_2"  # Secondary weapon
    OFF_HAND_2 = "off_hand_2"    # Secondary shield/off-hand
    
    # Set item slots
    NECK = "neck"
    WAIST = "waist"
    HANDS = "hands"
    FEET = "feet"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    BRACER_1 = "bracer_1"
    BRACER_2 = "bracer_2"


class SetBonus(BaseModel):
    """A bonus granted by equipping multiple pieces of a set."""
    
    pieces: int = Field(description="Number of pieces required for this bonus")
    description: str = Field(description="Description of the set's theme")
    bonuses: Dict[str, str] = Field(description="Bonuses at different piece thresholds")
    use_case: str = Field(description="Recommended use case for this set")
