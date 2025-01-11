"""
Pydantic models for stat-related data structures.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StatInfo(BaseModel):
    """Information about a specific stat."""
    name: str = Field(description="Name of the stat")
    description: str = Field(description="Description of what the stat does")
    category: str = Field(description="Category of the stat (offensive, defensive, utility)")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., percentage, flat)")
    min_value: Optional[float] = Field(None, description="Minimum possible value")
    max_value: Optional[float] = Field(None, description="Maximum possible value")
    sources: List[str] = Field(default_factory=list, description="Types of items that can provide this stat")


class StatBlock(BaseModel):
    """Character stat allocation."""
    
    strength: int = Field(
        ...,
        description="Strength stat value",
        ge=0
    )
    dexterity: int = Field(
        ...,
        description="Dexterity stat value",
        ge=0
    )
    intelligence: int = Field(
        ...,
        description="Intelligence stat value",
        ge=0
    )
    vitality: int = Field(
        ...,
        description="Vitality stat value",
        ge=0
    )


class StatCondition(BaseModel):
    """A condition that must be met for a stat value to apply."""

    description: str = Field(
        ...,
        description="Description of the condition"
    )
    trigger: Optional[str] = Field(
        None,
        description="Event or state that triggers the condition"
    )


class StatValue(BaseModel):
    """A single stat value with its conditions and properties."""

    conditions: List[StatCondition] = Field(
        default_factory=list,
        description="Conditions that must be met for this value"
    )
    value: float = Field(
        ...,
        description="The numeric value of the stat"
    )
    unit: str = Field(
        ...,
        description="Unit of measurement (e.g., 'percentage', 'flat')"
    )
    scaling: bool = Field(
        False,
        description="Whether this value scales with other stats"
    )


class StatSource(BaseModel):
    """A source of a stat (e.g., a gem or essence)."""

    name: str = Field(
        ...,
        description="Name of the source item"
    )
    stars: Optional[int] = Field(
        None,
        description="Star rating of the source (for gems)"
    )
    base_values: List[StatValue] = Field(
        default_factory=list,
        description="Base stat values provided"
    )
    rank_10_values: List[StatValue] = Field(
        default_factory=list,
        description="Stat values at rank 10"
    )
    conditions: List[StatCondition] = Field(
        default_factory=list,
        description="Global conditions for all values"
    )
    rank_10_conditions: List[StatCondition] = Field(
        default_factory=list,
        description="Additional conditions at rank 10"
    )

    @property
    def has_rank_10_bonus(self) -> bool:
        """Check if this source has rank 10 bonuses."""
        return bool(self.rank_10_values or self.rank_10_conditions)


class StatCategory(BaseModel):
    """Collection of stat sources by type."""
    
    gems: List[StatSource] = Field(
        default_factory=list,
        description="Gem sources for this stat"
    )


class GameStats(BaseModel):
    """Complete collection of game stats and their sources."""

    critical_hit_chance: StatCategory = Field(
        default_factory=StatCategory,
        description="Sources affecting critical hit chance"
    )
    damage_increase: StatCategory = Field(
        default_factory=StatCategory,
        description="Sources affecting damage increase"
    )
    attack_speed: StatCategory = Field(
        default_factory=StatCategory,
        description="Sources affecting attack speed"
    )
    movement_speed: StatCategory = Field(
        default_factory=StatCategory,
        description="Sources affecting movement speed"
    )
    life: StatCategory = Field(
        default_factory=StatCategory,
        description="Sources affecting life/health"
    )
