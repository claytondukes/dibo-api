"""Build configuration schemas for the DIBO API.

This module defines the data models for character builds, including equipment,
gems, and skill configurations.
"""
from typing import Dict, List, Optional
from pydantic import Field

from ..base import GameDataModel
from ..equipment import EquipmentSlot
from ..gems import GemConfig
from ..stats import StatBlock


class BuildConfig(GameDataModel):
    """Configuration for a character build."""
    
    version: str = Field(
        ...,
        description="Build version identifier"
    )
    name: str = Field(
        ...,
        description="Name of the build",
        min_length=1,
        max_length=100
    )
    class_type: str = Field(
        ...,
        description="Character class type"
    )
    equipment: Dict[EquipmentSlot, str] = Field(
        ...,
        description="Equipment configuration keyed by slot"
    )
    gems: Dict[str, GemConfig] = Field(
        ...,
        description="Gem configurations keyed by socket ID"
    )
    stats: StatBlock = Field(
        ...,
        description="Character stat allocation"
    )
    description: Optional[str] = Field(
        None,
        description="Optional build description",
        max_length=2000
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Build tags for categorization"
    )


class BuildSummary(GameDataModel):
    """Summary information for a build."""
    
    id: str = Field(
        ...,
        description="Unique identifier for the build"
    )
    version: str = Field(
        ...,
        description="Build version"
    )
    name: str = Field(
        ...,
        description="Build name"
    )
    class_type: str = Field(
        ...,
        description="Character class"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Build tags"
    )
    created_at: str = Field(
        ...,
        description="ISO timestamp of build creation"
    )
    updated_at: str = Field(
        ...,
        description="ISO timestamp of last update"
    )
