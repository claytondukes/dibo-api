"""
Pydantic models for gem-related data structures.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator


class GemCondition(BaseModel):
    """A condition for a gem effect."""
    type: str
    text: str
    trigger: Optional[str] = None
    state: Optional[str] = None
    threshold: Optional[float] = None
    cooldown: Optional[Union[str, float]] = None

    @field_validator('cooldown')
    def convert_cooldown_to_string(cls, v):
        """Convert cooldown to string if it's a float."""
        if isinstance(v, float):
            return str(v)
        return v


class GemEffect(BaseModel):
    """Represents a single effect of a gem."""
    
    type: str = Field(..., description="Type of effect (e.g., stat_effect, proc_effect)")
    text: str = Field(..., description="Description of the effect")
    conditions: List[GemCondition] = Field(default_factory=list, description="Conditions for the effect")


class GemStatValue(BaseModel):
    """A single stat value for a gem."""
    conditions: List[GemCondition] = Field(default_factory=list)
    value: Optional[float] = None
    unit: str = "percentage"
    scaling: bool = False


class GemStat(BaseModel):
    """Stat boost data for a gem."""
    name: str
    stars: str
    base_values: List[GemStatValue] = Field(default_factory=list)
    rank_10_values: List[GemStatValue] = Field(default_factory=list)
    conditions: List[GemCondition] = Field(default_factory=list)
    rank_10_conditions: List[GemCondition] = Field(default_factory=list)


class GemStatsByType(BaseModel):
    """Stat boosts grouped by stat type."""
    gems: List[GemStat] = Field(default_factory=list)
    essences: List[Any] = Field(default_factory=list)


class GemSynergy(BaseModel):
    """A condition for a gem synergy."""
    type: str
    text: str
    trigger: Optional[str] = None
    state: Optional[str] = None
    threshold: Optional[float] = None
    cooldown: Optional[Union[str, float]] = None

    @field_validator('cooldown')
    def convert_cooldown_to_string(cls, v):
        """Convert cooldown to string if it's a float."""
        if isinstance(v, float):
            return str(v)
        return v


class GemSynergyGroup(BaseModel):
    """A group of gems that share a synergy type."""
    gems: List[str] = Field(default_factory=list)
    essences: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    conditions: Dict[str, List[GemSynergy]] = Field(default_factory=dict)


class GemRankStats(BaseModel):
    """Stats for a specific gem rank."""
    
    damage_increase: Optional[List[GemStatValue]] = Field(None)
    critical_hit_chance: Optional[List[GemStatValue]] = Field(None)
    movement_speed: Optional[List[GemStatValue]] = Field(None)
    attack_speed: Optional[List[GemStatValue]] = Field(None)
    life: Optional[List[GemStatValue]] = Field(None)


class GemRank(BaseModel):
    """Represents a single rank of a gem."""
    
    effects: List[GemEffect] = Field(..., description="Effects at this rank")
    stats: GemRankStats = Field(..., description="Stats at this rank")


class GemProgression(BaseModel):
    """Represents the progression data for a gem."""
    
    base_rank: GemRank = Field(..., description="Base rank (1) data")
    max_rank: GemRank = Field(..., description="Maximum rank (10) data")


class GemConfig(BaseModel):
    """Configuration for a gem in a build."""
    
    type: str = Field(
        ...,
        description="Type of gem"
    )
    level: int = Field(
        ...,
        description="Level of the gem",
        ge=1,
        le=10
    )


class Gem(BaseModel):
    """Represents a single gem in the game."""
    
    stars: int = Field(..., description="Star rating of the gem (1, 2, or 5)", alias="Stars")
    name: str = Field(..., description="Name of the gem", alias="Name")
    base_effect: str = Field(
        ...,
        description="Base effect of the gem at rank 1",
        alias="BaseEffect"
    )
    rank_10_effect: Optional[str] = Field(
        None,
        description="Effect of the gem at rank 10",
        alias="Rank 10 Effect"
    )
    owned_rank: Optional[int] = Field(
        None,
        description="Current rank of the owned gem",
        alias="Owned Rank"
    )
    quality: Optional[int] = Field(
        None,
        description="Quality rating for 5-star gems (1-5)",
        alias="Quality (if 5 star)"
    )

    @field_validator('stars')
    def validate_stars(cls, v: Union[str, int]) -> int:
        """Convert stars to integer and validate."""
        if isinstance(v, str):
            v = int(v)
        if v not in {1, 2, 5}:
            raise ValueError("Star rating must be 1, 2, or 5")
        return v


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
