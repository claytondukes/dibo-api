"""Data models for game data."""

from enum import Enum
from typing import Dict, List, Optional, TypeVar, Generic
import json
from pydantic import BaseModel, Field, RootModel
from your_module import get_settings, logger  # Import get_settings and logger from your module

class BuildCategory(str, Enum):
    """Categories for game elements."""
    
    def __new__(cls):
        # Get categories from build types data
        data_dir = get_settings().DATA_DIR
        build_types_path = data_dir / "build_types.json"
        
        if not build_types_path.is_file():
            return super().__new__(cls, "UNKNOWN")
            
        try:
            with build_types_path.open() as f:
                data = json.load(f)
                
            # Extract unique categories from terms
            categories = set()
            for build_type in data.get("build_types", {}).values():
                for focus_type in build_type.values():
                    categories.update(
                        term.split()[0].upper() 
                        for term in focus_type.get("terms", [])
                    )
                    
            # Create enum members
            values = {}
            for category in sorted(categories):
                values[category] = category.lower()
                
            return str.__new__(cls, values)
            
        except Exception as e:
            logger.error(f"Error loading build categories: {e}")
            return super().__new__(cls, "UNKNOWN")


class GemBase(BaseModel):
    """Base gem information."""

    name: str = Field(..., description="Name of the gem")
    stars: int = Field(..., description="Star rating (1, 2, or 5)")
    base_effect: str = Field(..., description="Base effect description")
    rank_10_effect: Optional[str] = Field(
        None,
        description="Effect at rank 10 if available"
    )
    categories: List[BuildCategory] = Field(
        ...,
        description="Categories this gem belongs to"
    )


class Gem(GemBase):
    """Gem information with rank and quality."""

    rank: int = Field(..., description="Current rank of the gem")
    quality: Optional[int] = Field(None, description="Quality level if applicable")
    aux_gem: Optional[str] = Field(None, description="Name of auxiliary gem if any")


class SetBonus(BaseModel):
    """Equipment set bonus information."""

    pieces: int = Field(..., description="Number of pieces required")
    bonus: str = Field(..., description="Bonus description")


class EquipmentSet(BaseModel):
    """Equipment set information."""

    name: str = Field(..., description="Name of the set")
    description: str = Field(..., description="Set description")
    bonuses: Dict[str, str] = Field(
        ...,
        description="Bonuses keyed by piece count"
    )
    use_case: str = Field(..., description="Recommended use case")


class Skill(BaseModel):
    """Skill information."""

    name: str = Field(..., description="Name of the skill")
    description: str = Field(..., description="Skill description")
    cooldown: Optional[float] = Field(
        None,
        description="Cooldown in seconds if applicable"
    )
    categories: List[BuildCategory] = Field(
        ...,
        description="Categories this skill belongs to"
    )


class StatValue(BaseModel):
    """Value information for a stat modifier."""

    conditions: List[str] = Field(
        default_factory=list,
        description="Conditions required for this value"
    )
    value: float = Field(..., description="Numeric value of the modifier")
    unit: str = Field(..., description="Unit of measurement (e.g., 'percentage')")
    scaling: bool = Field(
        ...,
        description="Whether this value scales with some factor"
    )


class StatModifier(BaseModel):
    """Information about how an item modifies a stat."""

    name: str = Field(..., description="Name of the item")
    stars: Optional[str] = Field(None, description="Star rating if applicable")
    base_values: List[StatValue] = Field(
        default_factory=list,
        description="Values at base level"
    )
    rank_10_values: List[StatValue] = Field(
        default_factory=list,
        description="Values at rank 10"
    )
    conditions: List[str] = Field(
        default_factory=list,
        description="General conditions for this modifier"
    )
    rank_10_conditions: List[str] = Field(
        default_factory=list,
        description="Conditions at rank 10"
    )


class StatInfo(BaseModel):
    """Information about a game stat."""

    gems: List[StatModifier] = Field(
        default_factory=list,
        description="Gem modifiers for this stat"
    )
    essences: List[StatModifier] = Field(
        default_factory=list,
        description="Essence modifiers for this stat"
    )


StatsResponse = RootModel[Dict[str, StatInfo]]
"""Response model for stats endpoint."""


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
