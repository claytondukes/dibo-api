"""API routes for game modes and build types."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...builds.models import BuildType, BuildFocus


class GameModesResponse(BaseModel):
    """Response model for game modes endpoint."""
    
    game_modes: list[str] = Field(
        description="List of valid game modes",
        example=["raid", "pve", "pvp", "farm"]
    )
    build_types: list[str] = Field(
        description="List of valid build types",
        example=["dps", "survival", "buff"]
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
