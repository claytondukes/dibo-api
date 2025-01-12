"""Models for game synergies."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SynergyCondition(BaseModel):
    """A condition for a synergy."""
    
    type: str = Field(description="Type of condition")
    state: Optional[str] = Field(None, description="State for the condition")
    trigger: Optional[str] = Field(None, description="Trigger for the condition")
    text: str = Field(description="Text description of the condition")
    cooldown: Optional[float] = Field(None, description="Cooldown in seconds if applicable")
    threshold: Optional[float] = Field(None, description="Threshold value if applicable")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "type": "trigger",
                "state": None,
                "trigger": "on_hit",
                "text": "On hit",
                "cooldown": 1.0,
                "threshold": None
            }]
        }
    )


class SynergyGroup(BaseModel):
    """A group of items that share synergies."""
    
    gems: List[str] = Field(default_factory=list, description="Gems in this synergy")
    essences: List[str] = Field(default_factory=list, description="Essences in this synergy")
    skills: List[str] = Field(default_factory=list, description="Skills in this synergy")
    conditions: Dict[str, List[SynergyCondition]] = Field(
        default_factory=dict,
        description="Conditions for each item"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "gems": ["ruby", "sapphire"],
                "essences": ["fire", "water"],
                "skills": ["fireball", "ice_bolt"],
                "conditions": {
                    "ruby": [{
                        "type": "trigger",
                        "state": None,
                        "trigger": "on_hit",
                        "text": "On hit",
                        "cooldown": 1.0,
                        "threshold": None
                    }]
                }
            }]
        }
    )


class SynergyEffect(BaseModel):
    """Effect of a synergy."""
    
    description: str = Field(description="Description of the effect")
    value: float = Field(description="Value of the effect")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., percentage, flat)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "description": "Increases attack speed",
                "value": 10.0,
                "unit": "percentage"
            }]
        }
    )


class SynergyTier(BaseModel):
    """Tier of a synergy."""
    
    required: int = Field(description="Number of items required for this tier")
    effects: List[SynergyEffect] = Field(description="Effects at this tier")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "required": 3,
                "effects": [{
                    "description": "Increases attack speed",
                    "value": 10.0,
                    "unit": "percentage"
                }]
            }]
        }
    )


class Synergy(BaseModel):
    """A single synergy."""
    
    name: str = Field(description="Name of the synergy")
    description: str = Field(description="Description of the synergy")
    tiers: List[SynergyTier] = Field(description="Tiers of the synergy")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Attack Speed",
                "description": "Increases attack speed",
                "tiers": [{
                    "required": 3,
                    "effects": [{
                        "description": "Increases attack speed",
                        "value": 10.0,
                        "unit": "percentage"
                    }]
                }]
            }]
        }
    )


class GameSynergies(BaseModel):
    """Collection of game synergies."""
    
    critical_hit: Optional[SynergyGroup] = Field(None, description="Critical hit synergies")
    movement_speed: Optional[SynergyGroup] = Field(None, description="Movement speed synergies")
    damage_boost: Optional[SynergyGroup] = Field(None, description="Damage boost synergies")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "critical_hit": {
                    "gems": ["ruby", "sapphire"],
                    "essences": ["fire", "water"],
                    "skills": ["fireball", "ice_bolt"],
                    "conditions": {
                        "ruby": [{
                            "type": "trigger",
                            "state": None,
                            "trigger": "on_hit",
                            "text": "On hit",
                            "cooldown": 1.0,
                            "threshold": None
                        }]
                    }
                },
                "movement_speed": None,
                "damage_boost": None
            }]
        }
    )
