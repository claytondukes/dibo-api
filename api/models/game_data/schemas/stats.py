"""
Pydantic models for stat-related data structures.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class StatInfo(BaseModel):
    """Information about a specific stat."""
    
    name: str = Field(description="Name of the stat")
    description: str = Field(description="Description of what the stat does")
    category: str = Field(description="Category of the stat (offensive, defensive, utility)")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., percentage, flat)")
    min_value: Optional[float] = Field(None, description="Minimum possible value")
    max_value: Optional[float] = Field(None, description="Maximum possible value")
    sources: List[str] = Field(default_factory=list, description="Types of items that can provide this stat")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "name": "Attack Speed",
                "description": "Increases attack speed",
                "category": "offensive",
                "unit": "percentage",
                "min_value": 0.0,
                "max_value": 100.0,
                "sources": ["gems", "essences"]
            }]
        }
    )


class StatBlock(BaseModel):
    """Character stat allocation."""
    
    strength: int = Field(description="Strength stat value", ge=0)
    dexterity: int = Field(description="Dexterity stat value", ge=0)
    intelligence: int = Field(description="Intelligence stat value", ge=0)
    vitality: int = Field(description="Vitality stat value", ge=0)
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "strength": 10,
                "dexterity": 10,
                "intelligence": 10,
                "vitality": 10
            }]
        }
    )


class StatCondition(BaseModel):
    """A condition that must be met for a stat value to apply."""

    type: str = Field(description="Type of condition (trigger, state, etc.)")
    text: str = Field(description="Human-readable description of the condition")
    cooldown: Optional[float] = Field(None, description="Cooldown in seconds")
    threshold: Optional[float] = Field(None, description="Threshold value if applicable")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "type": "trigger",
                "text": "On hit",
                "cooldown": 1.0,
                "threshold": 0.5
            }]
        }
    )


class StatValue(BaseModel):
    """A single stat value with its conditions and properties."""

    value: float = Field(description="Base value of the stat")
    unit: Optional[str] = Field(None, description="Unit of measurement (percentage, flat, etc.)")
    conditions: List[StatCondition] = Field(default_factory=list, description="Conditions for the stat value")
    scaling: Optional[bool] = Field(None, description="Whether the value scales")
    min_value: Optional[float] = Field(None, description="Minimum value if scaling")
    max_value: Optional[float] = Field(None, description="Maximum value if scaling")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "value": 10.0,
                "unit": "percentage",
                "conditions": [],
                "scaling": True,
                "min_value": 0.0,
                "max_value": 100.0
            }]
        }
    )


class StatSource(BaseModel):
    """A source of a stat (e.g., a gem or essence)."""

    name: str = Field(description="Name of the source item")
    stars: Optional[int] = Field(None, description="Star rating of the source (for gems)")
    base_values: List[StatValue] = Field(default_factory=list, description="Base stat values provided")
    rank_10_values: List[StatValue] = Field(default_factory=list, description="Stat values at rank 10")
    conditions: List[StatCondition] = Field(default_factory=list, description="Global conditions for all values")
    rank_10_conditions: List[StatCondition] = Field(default_factory=list, description="Additional conditions at rank 10")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "name": "Ruby Gem",
                "stars": 5,
                "base_values": [],
                "rank_10_values": [],
                "conditions": [],
                "rank_10_conditions": []
            }]
        }
    )


class StatCategory(BaseModel):
    """Collection of stat sources by type."""
    
    gems: List[StatSource] = Field(default_factory=list, description="Gems affecting this stat")
    essences: List[StatSource] = Field(default_factory=list, description="Essences affecting this stat")
    skills: List[Dict[str, Any]] = Field(default_factory=list, description="Skills affecting this stat")
    description: Optional[str] = Field(None, description="Description of the stat category")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "gems": [],
                "essences": [],
                "skills": [],
                "description": "Stats affecting attack speed"
            }]
        }
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
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "critical_hit_chance": {},
                "damage_increase": {},
                "attack_speed": {},
                "movement_speed": {},
                "life": {}
            }]
        }
    )
