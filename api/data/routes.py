"""Game data routes."""

from typing import Optional, Union
from fastapi import APIRouter, Depends, Query, Response
from fastapi.exceptions import HTTPException
from starlette import status

from .models import (
    BuildCategory,
    GemBase,
    EquipmentSet,
    Skill,
    PaginatedResponse,
    StatInfo
)
from .service import DataService, get_data_service


router = APIRouter(prefix="/data", tags=["game-data"])


def add_cache_headers(response: Response) -> None:
    """Add cache headers to response.
    
    Since game data is static, we can cache it for a long time.
    """
    response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
    response.headers["Vary"] = "Accept-Encoding"


@router.get(
    "/gems",
    response_model=PaginatedResponse[GemBase],
    summary="List gems",
    description="List available gems with optional filtering"
)
async def list_gems(
    response: Response,
    stars: Optional[int] = Query(
        None,
        description="Filter by star rating (1, 2, or 5)",
        ge=1,
        le=5
    ),
    category: Optional[BuildCategory] = Query(
        None,
        description="Filter by category"
    ),
    page: int = Query(1, description="Page number", gt=0),
    per_page: int = Query(
        20,
        description="Items per page",
        gt=0,
        le=100
    ),
    data_service: DataService = Depends(get_data_service)
) -> PaginatedResponse[GemBase]:
    """List available gems with optional filtering."""
    if stars is not None and stars not in {1, 2, 5}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Stars must be 1, 2, or 5"
        )
    
    add_cache_headers(response)
    return data_service.get_gems(
        stars=stars,
        category=category,
        page=page,
        per_page=per_page
    )


@router.get(
    "/sets",
    response_model=PaginatedResponse[EquipmentSet],
    summary="List equipment sets",
    description="List available equipment sets with optional filtering"
)
async def list_sets(
    response: Response,
    pieces: Optional[int] = Query(
        None,
        description="Filter by number of pieces (2, 4, or 6)",
        ge=2,
        le=6
    ),
    page: int = Query(1, description="Page number", gt=0),
    per_page: int = Query(
        20,
        description="Items per page",
        gt=0,
        le=100
    ),
    data_service: DataService = Depends(get_data_service)
) -> PaginatedResponse[EquipmentSet]:
    """List available equipment sets."""
    if pieces is not None and pieces not in {2, 4, 6}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pieces must be 2, 4, or 6"
        )
    
    add_cache_headers(response)
    return data_service.get_sets(
        pieces=pieces,
        page=page,
        per_page=per_page
    )


@router.get(
    "/skills/{character_class}",
    response_model=PaginatedResponse[Skill],
    summary="List skills",
    description="List available skills for a character class"
)
async def list_skills(
    response: Response,
    character_class: str,
    category: Optional[BuildCategory] = Query(
        None,
        description="Filter by category"
    ),
    page: int = Query(1, description="Page number", gt=0),
    per_page: int = Query(
        20,
        description="Items per page",
        gt=0,
        le=100
    ),
    data_service: DataService = Depends(get_data_service)
) -> PaginatedResponse[Skill]:
    """List available skills for a character class."""
    add_cache_headers(response)
    return data_service.get_skills(
        character_class=character_class,
        category=category,
        page=page,
        per_page=per_page
    )


@router.get(
    "/stats",
    response_model=Union[dict[str, StatInfo], StatInfo],
    summary="Get stat relationships",
    description="""
    Get information about how different game elements affect various stats.
    Can optionally filter to a specific stat.
    """
)
async def list_stats(
    stat: Optional[str] = Query(
        None,
        description="Specific stat to retrieve"
    ),
    data_service: DataService = Depends(get_data_service)
):
    """List stat relationships with optional filtering."""
    return data_service.get_stats(stat=stat)
