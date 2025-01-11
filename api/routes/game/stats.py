"""API routes for game stats operations."""

from typing import Annotated, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas.stats import StatInfo


router = APIRouter(tags=["game"])


class StatListResponse(BaseModel):
    """Response model for stats listing endpoint."""
    stats: Dict[str, List[str]] = Field(
        description="Stats grouped by category (offensive, defensive, utility)"
    )


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/stats", response_model=StatListResponse)
async def list_stats(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> StatListResponse:
    """List all available game stats grouped by category.

    Args:
        data_manager: Game data manager instance

    Returns:
        Stats grouped by category

    Raises:
        HTTPException: If stats data cannot be loaded
    """
    try:
        logger.info("Getting all stat boosts")
        stats_data = await data_manager.get_stat_boosts()
            
        # Group stats by their categories
        categories = await data_manager.get_stat_categories()
        stats_by_category = {category: [] for category in categories}
        
        # Categorize stats based on metadata
        for stat_name, stat_info in stats_data.items():
            category = stat_info["category"]
            stats_by_category[category].append(stat_name)
            
        return StatListResponse(stats=stats_by_category)
        
    except Exception as e:
        logger.error(f"Error listing stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/{stat_name}", response_model=StatInfo)
async def get_stat_details(
    stat_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> StatInfo:
    """Get detailed information about a specific stat.

    Args:
        stat_name: Name of the stat to retrieve
        data_manager: Game data manager instance

    Returns:
        Detailed stat information

    Raises:
        HTTPException: If stat is not found or data cannot be loaded
    """
    try:
        logger.info(f"Getting stat boosts for: {stat_name}")
        stats_data = await data_manager.get_stat_boosts()
        if not stats_data or stat_name not in stats_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stat {stat_name} not found"
            )
            
        return StatInfo(
            name=stat_name,
            **stats_data[stat_name]
        )
            
    except Exception as e:
        logger.error(f"Error getting stat details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
