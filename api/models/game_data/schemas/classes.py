"""Pydantic models for class-related data."""

from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field


def get_available_classes() -> List[str]:
    """Get list of available character classes."""
    from api.core.config import get_settings
    
    classes_dir = get_settings().PROJECT_ROOT / "data" / "indexed" / "classes"
    if not classes_dir.exists():
        return ["barbarian"]  # Fallback default
    return [d.name for d in classes_dir.iterdir() if d.is_dir()]


# Create enum from available classes
CharacterClass = Enum('CharacterClass', {
    name.upper(): name.lower() 
    for name in get_available_classes()
})


class ClassListResponse(BaseModel):
    """Response model for class listing endpoint."""
    classes: List[str] = Field(description="List of available class names")


class ClassSkill(BaseModel):
    """Model for class skill information."""
    name: str = Field(description="Name of the skill")
    description: str = Field(description="Description of the skill")
    type: str = Field(description="Type of skill (e.g., basic, core, ultimate)")
    cooldown: Optional[float] = Field(None, description="Skill cooldown in seconds if applicable")
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
