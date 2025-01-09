"""API routes for game synergies."""

import json
import logging
from typing import Annotated, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from api.models.game_data.data_manager import GameDataManager
from api.models.game_data.schemas.synergies import GameSynergies, SynergyGroup


router = APIRouter(tags=["game"])
logger = logging.getLogger(__name__)


class SynergyListResponse(BaseModel):
    """Response model for synergy listing endpoint."""
    synergies: Dict[str, List[str]] = Field(
        description="Synergy types and their names"
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
        synergies_file = data_manager.base_path / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError("Synergies file not found")
            
        with open(synergies_file) as f:
            synergies_data = json.load(f)
            
        # Group synergies by type based on what they affect
        synergies_by_type = {
            "gems": [],
            "essences": [],
            "skills": []
        }
        
        for synergy_name, group in synergies_data.items():
            if group["gems"]:
                synergies_by_type["gems"].append(synergy_name)
            if group["essences"]:
                synergies_by_type["essences"].append(synergy_name)
            if group["skills"]:
                synergies_by_type["skills"].append(synergy_name)
                    
        return SynergyListResponse(synergies=synergies_by_type)
        
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
        synergies_file = data_manager.base_path / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError("Synergies file not found")
            
        with open(synergies_file) as f:
            synergies_data = json.load(f)
            
        if synergy_name not in synergies_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Synergy not found: {synergy_name}"
            )
            
        return synergies_data[synergy_name]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting synergy details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
