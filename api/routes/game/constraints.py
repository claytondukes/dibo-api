"""API routes for game constraints."""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas.constraints import GameConstraints


router = APIRouter(tags=["game"])
logger = logging.getLogger(__name__)


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/constraints", response_model=GameConstraints)
async def list_constraints(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> GameConstraints:
    """List all game constraints.

    Args:
        data_manager: Game data manager instance

    Returns:
        Game constraints data

    Raises:
        HTTPException: If constraints data cannot be loaded
    """
    try:
        logger.info("Getting game constraints")
        constraints = await data_manager.get_data("constraints")
        if not constraints:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Constraints data not found"
            )
            
        return GameConstraints(constraints=constraints)
        
    except Exception as e:
        logger.error(f"Error listing constraints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
