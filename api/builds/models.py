"""Build models and schemas."""

from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class BuildType(str, Enum):
    """Build type enumeration.
    
    Note: Build types are defined in build_types.json. This enum exists
    for type safety and documentation purposes only. The actual available
    build types are determined by the configuration file.
    """
    RAID = "raid"
    FARM = "farm"
    PVP = "pvp"
    
    @classmethod
    def _missing_(cls, value: str) -> None:
        """Handle unknown build types.
        
        Args:
            value: The build type string to convert
            
        Returns:
            None to indicate invalid value
            
        Note:
            This method intentionally returns None for unknown values.
            The BuildService will validate build types against the configuration
            and provide a proper error message if the type is not found.
        """
        return None


class BuildFocus(str, Enum):
    """Primary focus of the build."""
    
    DPS = "dps"
    SURVIVAL = "survival"
    BUFF = "buff"


class Gem(BaseModel):
    """Gem configuration."""
    
    name: str
    rank: int
    quality: Optional[int] = None


class Skill(BaseModel):
    """Skill configuration."""
    
    name: str
    essence: Optional[str] = None


class Equipment(BaseModel):
    """Equipment configuration."""
    
    name: str
    slot: str
    attributes: List[str] = Field(default_factory=list)
    essence: Optional[str] = None


class BuildStats(BaseModel):
    """Build performance statistics."""
    
    dps: float
    survival: float
    utility: float


class BuildRecommendation(BaseModel):
    """Build recommendation details."""
    
    gems: List[Gem]
    skills: List[Skill]
    equipment: List[Equipment]
    synergies: List[str] = Field(default_factory=list)


class BuildResponse(BaseModel):
    """Response model for build generation."""
    
    build: BuildRecommendation
    stats: BuildStats
    recommendations: List[str] = Field(default_factory=list)
    name: str
    type: BuildType
    focus: BuildFocus
    gear: Dict[str, Dict]
    sets: Dict[str, Dict]
    skills: Dict[str, Dict]
    paragon: Dict[str, Dict]
    gist_url: Optional[str] = None  # URL to view the saved build
    raw_url: Optional[str] = None   # URL to get the raw JSON
