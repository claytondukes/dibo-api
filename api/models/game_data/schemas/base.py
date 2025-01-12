"""
Base models for game data structures."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class GameDataModel(BaseModel):
    """Base model for all game data models."""
    
    model_config = ConfigDict(frozen=True, extra="forbid")


class GameDataMetadata(BaseModel):
    """Game data metadata."""
    
    last_updated: datetime = Field(description="Last update timestamp")
    version: str = Field(description="Data version")
    data_structure_version: str = Field(description="Data structure version")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "last_updated": "2025-01-03T21:19:08.263159",
                "version": "1.0",
                "data_structure_version": "1.0"
            }]
        }
    )


class GameDataCache(BaseModel):
    """Game data cache model."""
    
    metadata: GameDataMetadata = Field(description="Cache metadata")
    data: Dict[str, Any] = Field(description="Cached data by category")
    last_loaded: Optional[datetime] = Field(None, description="Last load timestamp")
    
    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        json_schema_extra={
            "examples": [{
                "metadata": {
                    "last_updated": "2025-01-03T21:19:08.263159",
                    "version": "1.0",
                    "data_structure_version": "1.0"
                },
                "data": {},
                "last_loaded": None
            }]
        }
    )


class BuildTypes(BaseModel):
    """Model for build types configuration."""
    
    build_types: Dict[str, Dict[str, Any]] = Field(
        description="Available build types and their configurations"
    )
    
    model_config = ConfigDict(frozen=True, extra="allow")
