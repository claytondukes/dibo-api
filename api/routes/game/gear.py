"""API routes for gear-related endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.models.game_data.data_manager import GameDataManager


router = APIRouter(tags=["game"])


class GearListResponse(BaseModel):
    """Response model for gear listing endpoint."""
    
    items: list[dict] = Field(description="List of gear items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")


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
        HTTPException: If invalid parameters are provided
    """
    # TODO: Implement this endpoint once gear data is available
    raise HTTPException(
        status_code=501,
        detail="Missing required data file: /data/indexed/equipment/gear.json"
    )
