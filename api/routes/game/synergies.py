"""API routes for game synergies."""

import logging
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas.synergies import SynergyGroup, GameSynergies


router = APIRouter(tags=["game"])
logger = logging.getLogger(__name__)


class SynergyListResponse(BaseModel):
    """Response model for synergy listing endpoint."""
    synergies: Dict[str, SynergyGroup] = Field(
        description="Map of synergy names to their groups"
    )


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/synergies", response_model=SynergyListResponse)
async def list_synergies(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> SynergyListResponse:
    """List all available synergy types and names.

    Args:
        data_manager: Game data manager instance

    Returns:
        Map of synergy types to their names

    Raises:
        HTTPException: If synergies data cannot be loaded
    """
    try:
        logger.info("Getting all synergies")
        synergies_file = data_manager.data_dir / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError("Synergies file not found")
            
        # Use Pydantic's model_validate_json instead of json.load
        synergies_data = GameSynergies.model_validate_json(synergies_file.read_text())
            
        return SynergyListResponse(synergies=synergies_data.synergies)
        
    except Exception as e:
        logger.error(f"Error listing synergies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/synergies/{synergy_name}", response_model=SynergyGroup)
async def get_synergy_details(
    synergy_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> SynergyGroup:
    """Get detailed information about a specific synergy.

    Args:
        synergy_name: Name of the synergy to retrieve
        data_manager: Game data manager instance

    Returns:
        Synergy group details

    Raises:
        HTTPException: If synergy is not found or data cannot be loaded
    """
    try:
        logger.info(f"Getting synergies for: {synergy_name}")
        synergies_file = data_manager.data_dir / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError("Synergies file not found")
            
        # Use Pydantic's model_validate_json instead of json.load
        synergies_data = GameSynergies.model_validate_json(synergies_file.read_text())
            
        if synergy_name not in synergies_data.synergies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Synergy not found: {synergy_name}"
            )
            
        return synergies_data.synergies[synergy_name]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting synergy details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
