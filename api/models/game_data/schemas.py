"""
Pydantic models for game data structures.

This module defines the schema models for various game data components,
ensuring type safety and validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator


class GameDataMetadata(BaseModel):
    """Metadata for game data versioning and updates."""
    
    last_updated: datetime = Field(
        ...,
        description="Timestamp of the last data update"
    )
    version: str = Field(
        ...,
        description="Version of the game data"
    )
    data_structure_version: str = Field(
        ...,
        description="Version of the data structure format"
    )


class GameDataCache(BaseModel):
    """In-memory cache for game data."""
    
    metadata: GameDataMetadata
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cached game data by category"
    )
    last_loaded: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the cache was last loaded"
    )


class GemsBySkill(BaseModel):
    """Model for gems organized by skill type."""

    movement: List[Any] = Field(default_factory=list)
    primary_attack: List[Any] = Field(default_factory=list, alias="primary attack")
    attack: List[Any] = Field(default_factory=list)
    summon: List[Any] = Field(default_factory=list)
    channeled: List[Any] = Field(default_factory=list)


class GemData(BaseModel):
    """Model for all gem data."""

    gems_by_skill: GemsBySkill = Field(..., description="Gems organized by skill type")


class SetBonus(BaseModel):
    """Model for set bonus thresholds and effects."""
    
    pieces: int = Field(ge=2, le=6, description="Number of pieces required")
    description: str = Field(description="Description of the set's focus")
    bonuses: Dict[str, str] = Field(description="Bonuses at different piece thresholds")
    use_case: str = Field(description="Recommended use case for the set")


class ClassEssence(BaseModel):
    """Model for class-specific essence modifications."""
    
    essence_name: str = Field(description="Display name of the essence")
    gear_slot: str = Field(description="Gear slot this essence can be applied to")
    modifies_skill: str = Field(description="Skill that this essence modifies")
    effect: str = Field(description="Description of the essence's effect")
    effect_type: Optional[str] = Field(None, description="Type of effect")
    effect_tags: Optional[List[str]] = Field(None, description="Tags describing the effect")


class GearItem(BaseModel):
    """Model for gear items."""
    
    name: str = Field(description="Display name of the gear item")
    slot: str = Field(description="Gear slot this item occupies")
    stats: Dict[str, str] = Field(description="Stats provided by the gear item")


class BuildTypes(BaseModel):
    """Model for build types configuration."""
    
    metadata: Dict[str, str] = Field(description="Build types metadata")
    build_types: Dict[str, Dict[str, Any]] = Field(
        description="Available build types and their configurations"
    )
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }


class StatCondition(BaseModel):
    """Model for stat conditions."""
    
    type: str = Field(description="Type of condition (state, trigger, etc)")
    state: Optional[str] = Field(None, description="State name if type is state")
    trigger: Optional[str] = Field(None, description="Trigger pattern if type is trigger")
    text: str = Field(description="Text pattern to match")
    threshold: Optional[float] = Field(None, description="Threshold value if applicable")
    description: Optional[str] = Field(None, description="Optional description of the condition")
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }


class StatValue(BaseModel):
    """Model for a stat value with conditions."""
    
    conditions: List[StatCondition] = Field(default_factory=list)
    value: Optional[float] = Field(None, description="Numeric value of the stat")
    min_value: Optional[float] = Field(None, description="Minimum value if scaling")
    max_value: Optional[float] = Field(None, description="Maximum value if scaling")
    unit: str = Field(description="Unit of measurement (percentage, flat, etc)")
    scaling: bool = Field(description="Whether the value scales with level")
    description: Optional[str] = Field(None, description="Optional description of the value")
    
    @model_validator(mode='after')
    def validate_value_fields(self) -> 'StatValue':
        """Ensure either value or min_value/max_value is present."""
        if self.value is None and (self.min_value is None or self.max_value is None):
            raise ValueError("Either value or both min_value and max_value must be set")
        return self
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }


class GemStat(BaseModel):
    """Model for gem stat modifications."""
    
    name: str = Field(description="Name of the gem")
    stars: str = Field(description="Star rating of the gem")
    base_values: List[StatValue] = Field(default_factory=list)
    rank_10_values: List[StatValue] = Field(default_factory=list)
    conditions: List[StatCondition] = Field(default_factory=list)
    rank_10_conditions: List[StatCondition] = Field(default_factory=list)
    description: Optional[str] = Field(None, description="Optional description of the gem")
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }


class StatCategory(BaseModel):
    """Model for a category of stats."""
    
    gems: List[GemStat] = Field(default_factory=list)
    description: Optional[str] = Field(None, description="Optional description of the category")
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }


class GameStats(BaseModel):
    """Model for game stats configuration."""
    
    metadata: Dict[str, str] = Field(description="Stats metadata")
    critical_hit_chance: StatCategory = Field(description="Critical hit chance modifiers")
    critical_hit_damage: StatCategory = Field(description="Critical hit damage modifiers")
    damage_increase: StatCategory = Field(description="Damage increase modifiers")
    attack_speed: StatCategory = Field(description="Attack speed modifiers")
    movement_speed: StatCategory = Field(description="Movement speed modifiers")
    life: StatCategory = Field(description="Life/health modifiers")
    description: Optional[str] = Field(None, description="Optional description of the game stats")
    
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "validate_assignment": False
    }
