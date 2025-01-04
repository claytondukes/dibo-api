"""Data models for game data."""

from enum import Enum
from typing import Dict, List, Optional, TypeVar, Generic

from pydantic import BaseModel, Field


class BuildCategory(str, Enum):
    """Categories for game elements."""

    MOVEMENT = "movement"
    PRIMARY_ATTACK = "primary_attack"
    ATTACK = "attack"
    DEFENSE = "defense"
    SUMMON = "summon"
    CHANNELED = "channeled"
    UTILITY = "utility"


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


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
