"""API routes for game stats operations."""

import json
from typing import Annotated, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

from api.models.game_data.data_manager import GameDataManager
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
        stats_file = data_manager.base_path / "stats.json"
        if not stats_file.exists():
            raise FileNotFoundError("Stats file not found")
            
        with open(stats_file) as f:
            stats_data = json.load(f)
            
        # Map stats to categories based on their effects
        stats_by_category = {
            "offensive": [],
            "defensive": [],
            "utility": []
        }
        
        # Categorize stats
        offensive_stats = ["critical_hit_chance", "damage_increase", "attack_speed"]
        defensive_stats = ["life", "armor", "resistance"]
        
        for stat_name in stats_data:
            if stat_name in offensive_stats:
                stats_by_category["offensive"].append(stat_name)
            elif stat_name in defensive_stats:
                stats_by_category["defensive"].append(stat_name)
            else:
                stats_by_category["utility"].append(stat_name)
            
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
        stats_file = data_manager.base_path / "stats.json"
        if not stats_file.exists():
            raise FileNotFoundError("Stats file not found")
            
        with open(stats_file) as f:
            stats_data = json.load(f)
            
        if stat_name not in stats_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stat not found: {stat_name}"
            )
            
        # Get stat category
        offensive_stats = ["critical_hit_chance", "damage_increase", "attack_speed"]
        defensive_stats = ["life", "armor", "resistance"]
        
        if stat_name in offensive_stats:
            category = "offensive"
        elif stat_name in defensive_stats:
            category = "defensive"
        else:
            category = "utility"
            
        # Get sources that provide this stat
        sources = []
        if stats_data[stat_name].get("gems"):
            sources.append("gems")
        if stats_data[stat_name].get("essences"):
            sources.append("essences")
            
        # Create stat info
        stat_info = {
            "name": stat_name,
            "description": f"Increases {stat_name.replace('_', ' ')}",  # TODO: Add proper descriptions
            "category": category,
            "unit": "percentage",  # Most stats are percentages
            "sources": sources
        }
            
        return StatInfo(**stat_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stat details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
