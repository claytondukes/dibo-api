"""
Pydantic models for gem-related data structures.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Gem(BaseModel):
    """Represents a single gem in the game."""
    
    stars: int = Field(..., alias="Stars", description="Star rating of the gem (1, 2, or 5)")
    name: str = Field(..., alias="Name", description="Name of the gem")
    base_effect: str = Field(
        ...,
        alias="Base Effect",
        description="Base effect of the gem at rank 1"
    )
    rank_10_effect: Optional[str] = Field(
        None,
        alias="Rank 10 Effect",
        description="Effect of the gem at rank 10"
    )
    owned_rank: Optional[int] = Field(
        None,
        alias="Owned Rank",
        description="Current rank of the owned gem"
    )
    quality: Optional[int] = Field(
        None,
        alias="Quality (if 5 star)",
        description="Quality rating for 5-star gems (1-5)"
    )

    @field_validator("stars", mode="before")
    def validate_stars(cls, v: str | int) -> int:
        """Validate star rating is 1, 2, or 5."""
        stars = int(v)
        if stars not in {1, 2, 5}:
            raise ValueError("Star rating must be 1, 2, or 5")
        return stars

    @field_validator("owned_rank", mode="before")
    def validate_owned_rank(cls, v: Optional[str | int]) -> Optional[int]:
        """Convert owned rank to integer."""
        if v is None:
            return None
        return int(v)

    @field_validator("quality", mode="before")
    def validate_quality(cls, v: Optional[str | int]) -> Optional[int]:
        """Convert quality to integer if present."""
        if v is None:
            return None
        return int(v)


class GemsBySkill(BaseModel):
    """Collection of gems organized by skill type."""
    
    movement: List[Gem] = Field(default_factory=list)
    primary_attack: List[Gem] = Field(
        default_factory=list,
        alias="primary attack"
    )
    attack: List[Gem] = Field(default_factory=list)
    summon: List[Gem] = Field(default_factory=list)
    channeled: List[Gem] = Field(default_factory=list)


class GemData(BaseModel):
    """Root model for gem data."""
    
    gems_by_skill: GemsBySkill = Field(
        ...,
        description="Gems organized by skill category"
    )
