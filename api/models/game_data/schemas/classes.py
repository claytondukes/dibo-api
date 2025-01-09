"""Pydantic models for class-related data."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClassSkill(BaseModel):
    """Model for class skill information."""
    name: str = Field(description="Name of the skill")
    description: str = Field(description="Description of the skill")
    type: str = Field(description="Type of skill (e.g., basic, core, ultimate)")
    cooldown: Optional[str] = Field(None, description="Skill cooldown if applicable")
    damage_type: Optional[str] = Field(None, description="Type of damage dealt")
    resource_cost: Optional[str] = Field(None, description="Resource cost to use skill")


class ClassInfo(BaseModel):
    """Model for class information."""
    name: str = Field(description="Name of the class")
    description: str = Field(description="Description of the class")
    primary_resource: str = Field(description="Primary resource type (e.g., fury, mana)")
    skills: Dict[str, List[ClassSkill]] = Field(
        description="Skills grouped by category (basic, core, ultimate)"
    )
    mechanics: List[str] = Field(description="Class-specific mechanics")
    recommended_playstyle: Optional[str] = Field(
        None, description="Recommended playstyle for the class"
    )
