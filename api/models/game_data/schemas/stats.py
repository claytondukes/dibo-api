"""
Pydantic models for stat-related data structures.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


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
    essences: List[StatSource] = Field(
        default_factory=list,
        description="Essence sources for this stat"
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
