"""API routes for game constraints."""

import json
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
        Map of constraint names to their values

    Raises:
        HTTPException: If constraints data cannot be loaded
    """
    try:
        constraints_file = data_manager.base_path / "constraints.json"
        if not constraints_file.exists():
            raise FileNotFoundError("Constraints file not found")
            
        with open(constraints_file) as f:
            constraints_data = json.load(f)
            
        return GameConstraints(constraints=constraints_data)
        
    except Exception as e:
        logger.error(f"Error listing constraints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
