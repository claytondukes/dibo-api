"""
Base schema models for game data.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class GameDataModel(BaseModel):
    """Base model for all game data entities."""
    
    model_config = ConfigDict(frozen=True, extra="forbid")


class GameDataMetadata(GameDataModel):
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
    categories: Optional[List[str]] = Field(
        default=None,
        description="List of available data categories"
    )


class GameDataCache(BaseModel):
    """In-memory cache for game data."""
    
    metadata: GameDataMetadata = Field(
        ...,
        description="Current metadata for the indexed data"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cached game data by category"
    )
    last_loaded: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the cache was last loaded"
    )
