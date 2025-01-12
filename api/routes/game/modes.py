"""API routes for game modes and build types."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, List

from ...builds.models import BuildType, BuildFocus


class GameModesResponse(BaseModel):
    """Response model for game modes."""
    
    game_modes: List[str] = Field(
        description="List of available game modes"
    )
    build_types: List[str] = Field(
        description="List of available build types"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "game_modes": ["raid", "pve", "pvp", "farm"],
                "build_types": ["dps", "survival", "buff"]
            }]
        }
    )


router = APIRouter(tags=["game"])


@router.get("/modes", response_model=GameModesResponse)
async def list_modes() -> GameModesResponse:
    """List valid game modes and build types.
    
    Returns:
        Valid game modes and build types
    """
    return GameModesResponse(
        game_modes=[mode.value for mode in BuildType],
        build_types=[focus.value for focus in BuildFocus]
    )
