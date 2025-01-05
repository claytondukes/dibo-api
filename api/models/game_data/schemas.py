"""
Pydantic models for game data structures.

This module defines the schema models for various game data components,
ensuring type safety and validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


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
