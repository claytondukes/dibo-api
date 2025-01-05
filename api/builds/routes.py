"""Build routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from ..auth.service import AuthService, get_auth_service
from ..core.config import get_settings
from .models import BuildFocus, BuildResponse, BuildType, BuildRecommendation
from .service import BuildService
from pathlib import Path

router = APIRouter(prefix="/builds", tags=["builds"])

# Initialize build service lazily
def get_build_service():
    """Get build service instance."""
    settings = get_settings()
    if settings.TESTING:
        if settings.TEST_DATA_DIR:
            return BuildService(data_dir=Path(settings.TEST_DATA_DIR))
        return None
    return BuildService()

_build_service = None

def get_service():
    """Get or create build service instance."""
    global _build_service
    if _build_service is None:
        _build_service = get_build_service()
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
    build_service: BuildService = Depends(get_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> BuildResponse:
    """Generate a build based on specified criteria."""
    if build_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Build service not available"
        )
    
    inventory = None
    if use_inventory:
        # Get user's inventory from GitHub gist
        inventory = await auth_service.get_inventory()
    
    return await build_service.generate_build(
        build_type=build_type,
        focus=focus,
        inventory=inventory
    )


@router.post(
    "/analyze",
    response_model=BuildResponse,
    summary="Analyze build",
    description="Analyze a specific build configuration for synergies and effectiveness"
)
async def analyze_build(
    build: BuildRecommendation,
    build_service: BuildService = Depends(get_service)
) -> BuildResponse:
    """Analyze a specific build configuration."""
    if build_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Build service not available"
        )
    
    return await build_service.analyze_build(build)
