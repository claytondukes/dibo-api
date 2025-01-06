"""
API routes for gem-related operations.
"""

import logging
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas.gems import Gem, GemData
from api.core.config import settings

router = APIRouter(prefix="/gems", tags=["gems"])
logger = logging.getLogger(__name__)


async def get_data_manager() -> GameDataManager:
    """Dependency to get the game data manager instance."""
    # TODO: In production, this should be a singleton or use dependency injection
    data_dir = settings.PROJECT_ROOT / "data" / "indexed"
    logger.info(f"Creating GameDataManager with data_dir: {data_dir}")
    return GameDataManager(data_dir=data_dir)


@router.get("/", response_model=List[Gem])
async def list_gems(
    skill_type: Optional[str] = Query(
        None,
        description="Filter gems by skill type (e.g., movement, attack)"
    ),
    stars: Optional[int] = Query(
        None,
        ge=1,
        le=5,
        description="Filter gems by star rating"
    ),
    data_manager: GameDataManager = Depends(get_data_manager)
) -> List[Gem]:
    """List all gems, optionally filtered by skill type and stars.

    Args:
        skill_type: Optional skill type to filter by
        stars: Optional star rating to filter by
        data_manager: Game data manager instance

    Returns:
        List of gems matching the filters
    """
    try:
        logger.info(f"Getting gem data with filters - skill_type: {skill_type}, stars: {stars}")
        gem_data = await data_manager.get_data("gems")
        if not gem_data:
            logger.warning("No gem data found")
            return []

        # Collect all gems across skill types
        all_gems = []
        logger.info(f"Got gem data: {gem_data}")
        for skill, gems in gem_data.gems_by_skill.model_dump(by_alias=True).items():
            logger.info(f"Processing skill: {skill} with {len(gems)} gems")
            if skill_type and skill != skill_type:
                continue
            for gem in gems:
                if stars and gem["Stars"] != stars:
                    continue
                all_gems.append(Gem.model_validate(gem))

        logger.info(f"Returning {len(all_gems)} gems")
        return all_gems

    except ValueError as e:
        logger.error(f"Error getting gems: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{gem_name}", response_model=Gem)
async def get_gem(
    gem_name: str,
    data_manager: GameDataManager = Depends(get_data_manager)
) -> Gem:
    """Get details for a specific gem by name.

    Args:
        gem_name: Name of the gem to retrieve
        data_manager: Game data manager instance

    Returns:
        Gem details if found

    Raises:
        HTTPException: If gem is not found
    """
    try:
        logger.info(f"Getting gem with name: {gem_name}")
        gem_data = await data_manager.get_data("gems")
        if not gem_data:
            logger.warning("No gem data available")
            raise HTTPException(status_code=404, detail="No gem data available")

        # Search for the gem across all skill types
        for skill, skill_gems in gem_data.gems_by_skill.model_dump(by_alias=True).items():
            logger.info(f"Searching in skill: {skill} with {len(skill_gems)} gems")
            for gem in skill_gems:
                # First validate the gem to ensure proper field mapping
                gem_model = Gem.model_validate(gem)
                if gem_model.name.lower() == gem_name.lower():
                    logger.info(f"Found gem: {gem_model}")
                    return gem_model

        logger.warning(f"Gem not found: {gem_name}")
        raise HTTPException(status_code=404, detail=f"Gem '{gem_name}' not found")

    except ValueError as e:
        logger.error(f"Error getting gem: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
