"""Pydantic models for game synergies."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SynergyCondition(BaseModel):
    """A condition for a synergy."""
    type: str = Field(description="Type of condition")
    state: Optional[str] = Field(None, description="State for the condition")
    trigger: Optional[str] = Field(None, description="Trigger for the condition")
    text: str = Field(description="Text description of the condition")


class SynergyGroup(BaseModel):
    """A group of items that share synergies."""
    gems: List[str] = Field(default_factory=list, description="Gems in this synergy")
    essences: List[str] = Field(default_factory=list, description="Essences in this synergy")
    skills: List[str] = Field(default_factory=list, description="Skills in this synergy")
    conditions: Dict[str, List[SynergyCondition]] = Field(
        default_factory=dict,
        description="Conditions for each item"
    )


class GameSynergies(BaseModel):
    """Collection of game synergies."""
    synergies: Dict[str, SynergyGroup] = Field(
        description="Map of synergy names to their groups"
    )
