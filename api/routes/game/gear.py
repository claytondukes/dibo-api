"""API routes for gear-related endpoints."""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from api.models.game_data.data_manager import GameDataManager


router = APIRouter(tags=["game"])


class GearListResponse(BaseModel):
    """Response model for gear listing endpoint."""
    
    items: list[dict] = Field(description="List of gear items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")


class EssenceResponse(BaseModel):
    """Response model for essence listing endpoint."""
    
    name: str = Field(description="Name of the essence")
    gear_slot: str = Field(description="Gear slot this essence can be applied to")
    modifies_skill: str = Field(description="Skill modified by this essence")
    effect: str = Field(description="Effect description")
    effect_type: Optional[str] = Field(None, description="Type of effect")
    effect_tags: Optional[List[str]] = Field(None, description="Tags describing the effect")


class EssenceListResponse(BaseModel):
    """Response model for essence listing endpoint."""
    
    essences: List[EssenceResponse] = Field(description="List of essences")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of essences")


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/gear", response_model=GearListResponse)
async def list_gear(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    class_name: Optional[str] = Query(None, alias="class"),
    slot: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    per_page: int = Query(20, gt=0, le=100)
) -> GearListResponse:
    """List available gear items with optional filtering.
    
    Args:
        data_manager: Game data manager instance
        class_name: Optional class name to filter by
        slot: Optional gear slot to filter by
        page: Page number (1-based)
        per_page: Items per page (max 100)
    
    Returns:
        Paginated list of gear items
        
    Raises:
        HTTPException: If invalid parameters are provided or data is missing
    """
    try:
        items, total = data_manager.get_gear_items(
            class_name=class_name,
            slot=slot,
            page=page,
            per_page=per_page
        )
        return GearListResponse(
            items=items,
            page=page,
            per_page=per_page,
            total=total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/gear/{class_name}/essences", response_model=EssenceListResponse)
async def list_class_essences(
    class_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    slot: Optional[str] = Query(None, description="Filter by gear slot"),
    skill: Optional[str] = Query(None, description="Filter by modified skill"),
    page: int = Query(1, gt=0, description="Page number"),
    per_page: int = Query(20, gt=0, le=100, description="Items per page")
) -> EssenceListResponse:
    """List available essences for a specific class.
    
    Args:
        class_name: Name of the class to get essences for
        data_manager: Game data manager instance
        slot: Optional gear slot to filter by
        skill: Optional skill to filter by
        page: Page number (1-based)
        per_page: Items per page (max 100)
    
    Returns:
        Paginated list of essences
        
    Raises:
        HTTPException: If class not found or invalid parameters
    """
    try:
        essences_data = data_manager.get_class_essences(
            class_name=class_name,
            slot=slot,
            skill=skill
        )
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_essences = list(essences_data.items())[start_idx:end_idx]
        
        # Convert to response format
        essences = [
            EssenceResponse(
                name=essence.essence_name,
                gear_slot=essence.gear_slot,
                modifies_skill=essence.modifies_skill,
                effect=essence.effect,
                effect_type=essence.effect_type,
                effect_tags=essence.effect_tags
            )
            for _, essence in paginated_essences
        ]
        
        return EssenceListResponse(
            essences=essences,
            page=page,
            per_page=per_page,
            total=len(essences_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
