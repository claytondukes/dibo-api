"""Essence data schemas."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .base import GameDataModel


class EssenceSkillInfo(BaseModel):
    """Information about a skill's essences."""
    description: str = Field(description="Description of the skill")
    essence_count: int = Field(description="Number of essences for this skill")


class EssenceMetadata(BaseModel):
    """Metadata for class essences."""
    version: str = Field(description="Version of the essence data")
    last_updated: str = Field(description="Last update timestamp")
    class_: str = Field(alias="class", description="Class name")
    total_essences: int = Field(description="Total number of essences")
    skills: Dict[str, EssenceSkillInfo] = Field(description="Skills and their essence counts")

    model_config = ConfigDict(populate_by_name=True)


class EssenceData(BaseModel):
    """Individual essence data."""
    essence_name: str = Field(description="Name of the essence")
    gear_slot: str = Field(description="Gear slot this essence applies to")
    modifies_skill: str = Field(description="Skill modified by this essence")
    effect: str = Field(description="Effect description")
    effect_type: Optional[str] = Field(None, description="Type of effect")
    effect_tags: Optional[List[str]] = Field(None, description="Tags describing the effect")


class EssenceIndexes(BaseModel):
    """Indexes for quick essence lookups."""
    by_slot: Dict[str, List[str]] = Field(description="Essences indexed by gear slot")


class ClassEssences(GameDataModel):
    """Class-specific essence data."""
    metadata: EssenceMetadata = Field(description="Essence metadata")
    essences: Dict[str, EssenceData] = Field(description="Essence definitions")
    indexes: EssenceIndexes = Field(description="Essence indexes")
