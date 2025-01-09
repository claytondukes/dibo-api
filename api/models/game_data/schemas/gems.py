"""
Pydantic models for gem-related data structures.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .base import GameDataModel


class GemCondition(BaseModel):
    """A condition for a gem effect."""
    type: str
    text: str
    conditions: List[Any] = Field(default_factory=list)


class GemEffect(BaseModel):
    """Represents a single effect of a gem."""
    type: str = Field(..., description="Type of effect (e.g., stat_effect, proc_effect)")
    text: str = Field(..., description="Description of the effect")
    conditions: List[GemCondition] = Field(default_factory=list, description="Conditions for the effect")


class GemStatValue(BaseModel):
    """A single stat value for a gem."""
    value: Optional[float] = None
    conditions: List[GemCondition] = Field(default_factory=list)
    context: Optional[str] = None


class GemRankStats(BaseModel):
    """Stats for a specific gem rank."""
    damage_increase: Optional[List[GemStatValue]] = None
    critical_hit_chance: Optional[List[GemStatValue]] = None
    movement_speed: Optional[List[GemStatValue]] = None
    attack_speed: Optional[List[GemStatValue]] = None
    life: Optional[List[GemStatValue]] = None


class GemRank(BaseModel):
    """Represents a single rank of a gem."""
    effects: List[GemEffect] = Field(..., description="Effects at this rank")
    stats: Dict[str, List[GemStatValue]] = Field(default_factory=dict, description="Stats at this rank")


class Gem(BaseModel):
    """Represents a single gem in the game."""
    
    stars: str = Field(..., description="Star rating of the gem (1, 2, or 5)", alias="Stars")
    name: str = Field(..., description="Name of the gem", alias="Name")
    ranks: Dict[str, GemRank] = Field(..., description="Effects at each rank")
    max_rank: int = Field(..., description="Maximum rank for this gem")
    magic_find: str = Field(..., description="Magic find value")
    max_effect: str = Field(..., description="Maximum effect description")
    base_effect: str = Field(default="", description="Base effect from rank 1")

    def __init__(self, **data):
        super().__init__(**data)
        if "1" in self.ranks and self.ranks["1"].effects:
            self.base_effect = self.ranks["1"].effects[0].text

    @field_validator('stars')
    def validate_stars(cls, v: Union[str, int]) -> str:
        """Convert stars to string and validate."""
        if isinstance(v, int):
            v = str(v)
        if v not in ["1", "2", "5"]:
            raise ValueError("Stars must be 1, 2, or 5")
        return v

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class GemsBySkill(BaseModel):
    """Collection of gems organized by skill type."""
    
    movement: List[str] = Field(default_factory=list)
    primary_attack: List[str] = Field(default_factory=list, alias="primary attack")
    attack: List[str] = Field(default_factory=list)
    damage: List[str] = Field(default_factory=list)
    summon: List[str] = Field(default_factory=list)
    defense: List[str] = Field(default_factory=list)
    channeling: List[str] = Field(default_factory=list)
    ultimate: List[str] = Field(default_factory=list)
    buff: List[str] = Field(default_factory=list)
    dash: List[str] = Field(default_factory=list)


class GemSkillMap(BaseModel):
    """Root model for gem data organized by skills."""
    gems_by_skill: GemsBySkill = Field(
        ...,
        description="Gems organized by skill category"
    )


class GemConfig(GameDataModel):
    """Configuration for a gem in a build."""
    
    name: str = Field(
        ...,
        description="Name of the gem"
    )
    rank: int = Field(
        ...,
        description="Rank of the gem",
        ge=1,
        le=10
    )
