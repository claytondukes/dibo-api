"""Build routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from ..auth.service import AuthService, get_auth_service
from .models import BuildFocus, BuildResponse, BuildType
from .service import BuildService


router = APIRouter(prefix="/builds", tags=["builds"])
_build_service = BuildService()


def get_build_service() -> BuildService:
    """Get BuildService instance."""
    return _build_service


@router.get(
    "/generate",
    response_model=BuildResponse,
    summary="Generate build",
    description="Generate an optimized build based on specified criteria"
)
async def generate_build(
    build_type: BuildType = Query(..., description="Type of build to generate"),
    focus: BuildFocus = Query(..., description="Primary focus of the build"),
    use_inventory: bool = Query(
        False,
        description="Whether to consider user's inventory"
    ),
    build_service: BuildService = Depends(get_build_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> BuildResponse:
    """Generate a build based on specified criteria."""
    inventory = None
    if use_inventory:
        # Get user's inventory from GitHub gist
        inventory = await auth_service.get_inventory()
    
    return await build_service.generate_build(
        build_type=build_type,
        focus=focus,
        inventory=inventory
    )
