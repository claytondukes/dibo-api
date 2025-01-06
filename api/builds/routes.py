"""Build routes."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
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


@router.post(
    "/generate",
    response_model=BuildResponse,
    summary="Generate build",
    description="Generate an optimized build based on specified criteria"
)
async def generate_build(
    build_type: BuildType = Query(..., description="Type of build to generate"),
    focus: BuildFocus = Query(..., description="Primary focus of the build"),
    save: bool = Query(False, description="Whether to save the build to a gist"),
    use_inventory: bool = Query(
        False,
        description="Whether to consider user's inventory"
    ),
    build_service: BuildService = Depends(get_service),
    auth_service: AuthService = Depends(get_auth_service),
    request: Request = None
) -> BuildResponse:
    """Generate a build based on specified criteria."""
    if build_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Build service not available"
        )
    
    inventory = None
    if use_inventory:
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization required to use inventory"
            )
        token = token.split(" ")[1]
        inventory = await auth_service.get_inventory_gist(token)
    
    # Generate the build
    build = await build_service.generate_build(
        build_type=build_type,
        focus=focus,
        character_class=inventory.get("profile", {}).get("class") if inventory else None,
        inventory=inventory
    )
    
    # Save build if requested
    if save:
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization required to save build"
            )
        token = token.split(" ")[1]
        
        # Save to a new gist
        gist_data = await auth_service.save_generated_build(token, build.dict())
        build.gist_url = gist_data["url"]
        build.raw_url = gist_data["raw_url"]
    
    return build


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


@router.get(
    "/{gist_id}",
    response_model=BuildResponse,
    summary="Get saved build",
    description="Get a previously saved build from a gist"
)
async def get_build(
    gist_id: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> BuildResponse:
    """Get a previously saved build."""
    # Get token from request
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required to fetch build"
        )
    token = token.split(" ")[1]
    
    # Get the build
    build_data = await auth_service.get_generated_build(token, gist_id)
    return BuildResponse(**build_data["build"])


@router.put(
    "/{gist_id}",
    response_model=BuildResponse,
    summary="Update saved build",
    description="Update a previously saved build in a gist"
)
async def update_build(
    gist_id: str,
    build_update: BuildResponse,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> BuildResponse:
    """Update a previously saved build."""
    # Get token from request
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required to update build"
        )
    token = token.split(" ")[1]
    
    # Update the build
    gist_data = await auth_service.save_generated_build(
        token, 
        gist_id,
        build_update.dict()
    )
    
    # Return updated build with URLs
    build_dict = build_update.dict()
    build_dict.update({
        "gist_url": f"https://gist.github.com/{gist_id}",
        "raw_url": f"https://gist.githubusercontent.com/raw/{gist_id}/build.json"
    })
    return BuildResponse(**build_dict)
