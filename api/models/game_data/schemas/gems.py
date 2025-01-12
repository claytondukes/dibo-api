"""
Pydantic models for gem-related data structures.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, RootModel
from .base import GameDataModel


class GemCondition(BaseModel):
    """A condition for a gem effect."""
    type: str = Field(description="Type of condition")
    description: str = Field(description="Description of the condition")
    state: Optional[str] = Field(default=None, description="State for state-type conditions")
    threshold: Optional[float] = Field(default=None, description="Threshold for numeric conditions")
    cooldown: Optional[float] = Field(default=None, description="Cooldown in seconds")
    trigger: Optional[str] = Field(default=None, description="Trigger for trigger-type conditions")

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class GemEffect(BaseModel):
    """Represents a single effect of a gem."""
    type: str = Field(description="Type of effect (e.g., stat_effect, proc_effect)")
    description: str = Field(description="Description of the effect")
    conditions: List[GemCondition] = Field(default_factory=list, description="Conditions for the effect")
    state: Optional[str] = Field(default=None, description="State for state-type effects")
    threshold: Optional[float] = Field(default=None, description="Threshold for numeric effects")
    cooldown: Optional[float] = Field(default=None, description="Cooldown in seconds")
    trigger: Optional[str] = Field(default=None, description="Trigger for trigger-type effects")

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class GemStatValue(BaseModel):
    """A single stat value for a gem."""
    value: Optional[float] = Field(default=None, description="The stat value")
    min_value: Optional[float] = Field(default=None, description="Minimum value for scaling stats")
    max_value: Optional[float] = Field(default=None, description="Maximum value for scaling stats")
    conditions: List[GemCondition] = Field(default_factory=list, description="Conditions for the stat value")
    context: Optional[str] = Field(default=None, description="Context for the stat value")
    state: Optional[str] = Field(default=None, description="State for state-type values")
    threshold: Optional[float] = Field(default=None, description="Threshold for numeric values")
    cooldown: Optional[float] = Field(default=None, description="Cooldown in seconds")
    trigger: Optional[str] = Field(default=None, description="Trigger for trigger-type values")
    unit: Optional[str] = Field(default=None, description="Unit for the value (e.g., percentage)")
    scaling: Optional[bool] = Field(default=None, description="Whether the value scales")

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class GemRankStats(BaseModel):
    """Stats for a specific gem rank."""
    damage_increase: Optional[List[GemStatValue]] = Field(default=None, description="Damage increase stats")
    critical_hit_chance: Optional[List[GemStatValue]] = Field(default=None, description="Critical hit chance stats")
    movement_speed: Optional[List[GemStatValue]] = Field(default=None, description="Movement speed stats")
    attack_speed: Optional[List[GemStatValue]] = Field(default=None, description="Attack speed stats")
    life: Optional[List[GemStatValue]] = Field(default=None, description="Life stats")
    damage_reduction: Optional[List[GemStatValue]] = Field(default=None, description="Damage reduction stats")

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class GemRank(BaseModel):
    """Represents a single rank of a gem."""
    effects: List[GemEffect] = Field(description="Effects at this rank")
    stats: Dict[str, List[GemStatValue]] = Field(default_factory=dict, description="Stats at this rank")

    model_config = ConfigDict(
        str_to_lower=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        coerce_numbers_to_str=True
    )


class Gem(BaseModel):
    """Represents a single gem in the game."""
    
    stars: str = Field(description="Star rating of the gem (1, 2, or 5)", alias="Stars")
    name: str = Field(description="Name of the gem")  
    ranks: Dict[str, GemRank] = Field(description="Effects at each rank")
    max_rank: int = Field(description="Maximum rank for this gem")
    magic_find: str = Field(description="Magic find value")
    max_effect: Optional[str] = Field(default=None, description="Maximum effect description")
    base_effect: str = Field(default="", description="Base effect from rank 1")

    def __init__(self, **data):
        super().__init__(**data)
        if "1" in self.ranks and self.ranks["1"].effects:
            self.base_effect = self.ranks["1"].effects[0].description

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


class GemRegistry(RootModel[Dict[str, Gem]]):
    """Collection of all gems in the game."""

    @model_validator(mode='before')
    def set_gem_names(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set the name field for each gem from its key."""
        if not isinstance(values, dict):
            return values
        
        for key, gem_data in values.items():
            if isinstance(gem_data, dict):
                gem_data['name'] = key
                # Set default max_effect if not present
                if 'max_effect' not in gem_data:
                    gem_data['max_effect'] = None
        
        return values

    def __iter__(self):
        """Iterate over all gems."""
        return iter(self.root)

    def __getitem__(self, key: str) -> Gem:
        """Get a gem by name."""
        return self.root[key]

    def __contains__(self, key: str) -> bool:
        """Check if a gem exists."""
        return key in self.root

    def get(self, key: str, default: Any = None) -> Optional[Gem]:
        """Get a gem by name with a default value."""
        return self.root.get(key, default)


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
