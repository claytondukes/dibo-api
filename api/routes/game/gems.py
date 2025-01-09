"""
API routes for gem-related operations.
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from api.models.game_data.data_manager import GameDataManager
from api.models.game_data.schemas.gems import (
    Gem, GemData, GemProgression, GemsBySkill, GemStatsByType, GemStatValue, GemSynergyGroup,
    GemRank, GemEffect, GemRankStats
)
from api.core.config import settings

router = APIRouter(prefix="/gems", tags=["gems"])
logger = logging.getLogger(__name__)


async def get_data_manager() -> GameDataManager:
    """Dependency to get the game data manager instance."""
    # TODO: In production, this should be a singleton or use dependency injection
    base_path = settings.PROJECT_ROOT / "data" / "indexed"
    logger.info(f"Creating GameDataManager with base_path: {base_path}")
    return GameDataManager(base_path=base_path)


def transform_gem_data(gem_dict: dict) -> dict:
    """Transform gem data to match our schema."""
    return {
        "Stars": gem_dict.get("Stars"),
        "Name": gem_dict.get("Name"),
        "Base Effect": gem_dict.get("Base Effect"),
        "Rank 10 Effect": gem_dict.get("Rank 10 Effect"),
        "Owned Rank": gem_dict.get("Owned Rank"),
        "Quality (if 5 star)": gem_dict.get("Quality (if 5 star)")
    }


def get_gem_from_progression(gem_name: str, progression_data: dict) -> Optional[dict]:
    """Get gem data from progression data."""
    if gem_name not in progression_data:
        return None
    
    prog = progression_data[gem_name]
    rank_1 = prog["ranks"]["1"]
    rank_10 = prog["ranks"]["10"]
    
    return {
        "Stars": prog["stars"],
        "Name": gem_name,
        "BaseEffect": rank_1["effects"][0]["text"] if rank_1["effects"] else None,
        "Rank 10 Effect": rank_10["effects"][0]["text"] if rank_10["effects"] else None,
        "Owned Rank": "1",  # Default to rank 1
        "Quality (if 5 star)": None
    }


def convert_stats_to_pascal_case(stats: dict) -> dict:
    """Convert snake_case stat keys to PascalCase."""
    key_map = {
        "attack_speed": "AttackSpeed",
        "critical_hit_chance": "CriticalHitChance",
        "critical_hit_damage": "CriticalHitDamage",
        "damage_increase": "DamageIncrease",
        "movement_speed": "MovementSpeed",
        "life": "Life"
    }
    
    result = {}
    for k, v in stats.items():
        new_key = key_map.get(k, k)
        
        # Convert gems to Gems
        if isinstance(v, dict) and "gems" in v:
            v = {
                "Gems": v["gems"],
                "Essences": v.get("essences", [])
            }
            
        result[new_key] = v
        
    return result


def convert_synergies_to_pascal_case(synergies: dict) -> dict:
    """Convert snake_case synergy keys to PascalCase."""
    key_map = {
        "critical_hit": "CriticalHit",
        "damage_boost": "DamageBoost",
        "movement_speed": "MovementSpeed",
        "control": "Control"
    }
    
    result = {}
    for k, v in synergies.items():
        new_key = key_map.get(k, k)
        
        # Convert gems to Gems
        if isinstance(v, dict):
            v = {
                "Gems": v.get("gems", []),
                "Essences": v.get("essences", []),
                "Skills": v.get("skills", []),
                "Conditions": v.get("conditions", {})
            }
            
        result[new_key] = v
        
    return result


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
        
        # Load gems data
        gems_file = data_manager.base_path / "gems" / "gems.json"
        if not gems_file.exists():
            raise FileNotFoundError(f"Gems data file not found: {gems_file}")
            
        with open(gems_file) as f:
            progression_data = json.load(f)
            
        # Load skill mapping
        skillmap_file = data_manager.base_path / "gems" / "gem_skillmap.json"
        if not skillmap_file.exists():
            raise FileNotFoundError(f"Gem skill mapping file not found: {skillmap_file}")
            
        with open(skillmap_file) as f:
            skillmap_data = json.load(f)
            
        # Collect all gems
        all_gems = []
        skill_types = skillmap_data.get("gems_by_skill", {})
        if skill_type:
            skill_type = skill_type.lower().replace(" ", "_")
            # Only include gems from the specified skill type
            for skill_name, skill_gems in skill_types.items():
                if skill_type in skill_name.lower():
                    for gem_name in skill_gems:
                        if gem_name in progression_data:
                            all_gems.append(get_gem_from_progression(gem_name, progression_data))
        else:
            # Include all gems
            for skill_gems in skill_types.values():
                for gem_name in skill_gems:
                    if gem_name in progression_data:
                        all_gems.append(get_gem_from_progression(gem_name, progression_data))
        
        # Apply star filter if specified
        if stars:
            all_gems = [gem for gem in all_gems if int(gem["Stars"]) == stars]
        
        # Convert to Gem models
        return [Gem.model_validate(gem) for gem in all_gems if gem]
        
    except Exception as e:
        logger.error(f"Error getting gems: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def list_gem_stats(
    data_manager: GameDataManager = Depends(get_data_manager)
) -> dict:
    """Get all gem stat boosts.

    Args:
        data_manager: Game data manager instance

    Returns:
        All gem stat boosts
    """
    try:
        logger.info("Getting all gem stat boosts")
        
        # Load gem stats data
        stats_file = data_manager.base_path / "gems" / "stat_boosts.json"
        if not stats_file.exists():
            raise FileNotFoundError(f"Gem stats file not found: {stats_file}")
            
        with open(stats_file) as f:
            stats_data = json.load(f)
            
        return convert_stats_to_pascal_case(stats_data)
            
    except Exception as e:
        logger.error(f"Error getting gem stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/synergies")
async def list_gem_synergies(
    data_manager: GameDataManager = Depends(get_data_manager)
) -> dict:
    """Get all gem synergies.

    Args:
        data_manager: Game data manager instance

    Returns:
        All gem synergies
    """
    try:
        logger.info("Getting all gem synergies")
        
        # Load gem synergies data
        synergies_file = data_manager.base_path / "gems" / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError(f"Gem synergies file not found: {synergies_file}")
            
        with open(synergies_file) as f:
            synergies_data = json.load(f)
            
        return convert_synergies_to_pascal_case(synergies_data)
            
    except Exception as e:
        logger.error(f"Error getting gem synergies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/skills", response_model=List[str])
async def list_gem_skills(
    data_manager: GameDataManager = Depends(get_data_manager)
) -> List[str]:
    """List all available gem skill types.

    Args:
        data_manager: Game data manager instance

    Returns:
        List of unique skill types
    """
    try:
        logger.info("Getting all gem skill types")
        
        # Load skill mapping
        skillmap_file = data_manager.base_path / "gems" / "gem_skillmap.json"
        if not skillmap_file.exists():
            raise FileNotFoundError(f"Gem skill mapping file not found: {skillmap_file}")
            
        with open(skillmap_file) as f:
            skillmap_data = json.load(f)
            
        # Get unique skill types
        return list(skillmap_data.get("gems_by_skill", {}).keys())
        
    except Exception as e:
        logger.error(f"Error getting gem skill types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
        logger.info(f"Getting gem data for: {gem_name}")
        
        # Load gems data
        gems_file = data_manager.base_path / "gems" / "gems.json"
        if not gems_file.exists():
            raise FileNotFoundError(f"Gems data file not found: {gems_file}")
            
        with open(gems_file) as f:
            progression_data = json.load(f)
            
        # Load skill mapping
        skillmap_file = data_manager.base_path / "gems" / "gem_skillmap.json"
        if not skillmap_file.exists():
            raise FileNotFoundError(f"Gem skill mapping file not found: {skillmap_file}")
            
        with open(skillmap_file) as f:
            skillmap_data = json.load(f)
            
        # Search for gem by name
        # Case-insensitive lookup
        actual_key = next(
            (k for k in progression_data.keys() if k.lower() == gem_name.lower()),
            None
        )
        if actual_key:
            gem_data = get_gem_from_progression(actual_key, progression_data)
            if gem_data:
                return Gem.model_validate(gem_data)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gem not found: {gem_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gem {gem_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{gem_name}/stats")
async def get_gem_stats(
    gem_name: str,
    data_manager: GameDataManager = Depends(get_data_manager)
) -> dict:
    """Get stat boosts for a specific gem.

    Args:
        gem_name: Name of the gem to retrieve stats for
        data_manager: Game data manager instance

    Returns:
        Gem stat boosts if found

    Raises:
        HTTPException: If gem or stats data is not found
    """
    try:
        logger.info(f"Getting stats for gem: {gem_name}")
        
        # Load gem stats data
        stats_file = data_manager.base_path / "gems" / "stat_boosts.json"
        if not stats_file.exists():
            raise FileNotFoundError(f"Gem stats file not found: {stats_file}")
            
        with open(stats_file) as f:
            stats_data = json.load(f)
            
        # Find stats for the gem
        gem_stats = {}
        for stat_type, stat_data in stats_data.items():
            if not stat_data.get("gems"):
                continue
                
            for gem in stat_data["gems"]:
                if gem["name"].lower() == gem_name.lower():
                    # Use base_values if available, otherwise use rank_10_values
                    values = gem.get("base_values", [])
                    if not values and "rank_10_values" in gem:
                        values = gem["rank_10_values"]
                        
                    gem_stats[stat_type] = values
                    
        if not gem_stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No stats found for gem {gem_name}"
            )
            
        return convert_stats_to_pascal_case(gem_stats)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for gem {gem_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{gem_name}/synergies")
async def get_gem_synergies(
    gem_name: str,
    data_manager: GameDataManager = Depends(get_data_manager)
) -> dict:
    """Get synergies for a specific gem.

    Args:
        gem_name: Name of the gem to retrieve synergies for
        data_manager: Game data manager instance

    Returns:
        Gem synergies if found

    Raises:
        HTTPException: If gem or synergies data is not found
    """
    try:
        logger.info(f"Getting synergies for gem: {gem_name}")
        
        # Load gem synergies data
        synergies_file = data_manager.base_path / "gems" / "synergies.json"
        if not synergies_file.exists():
            raise FileNotFoundError(f"Gem synergies file not found: {synergies_file}")
            
        with open(synergies_file) as f:
            synergies_data = json.load(f)
            
        # Find synergies for the gem
        gem_synergies = {}
        for synergy_type, synergy_data in synergies_data.items():
            if not synergy_data.get("gems"):
                continue
                
            if gem_name.lower() in [g.lower() for g in synergy_data["gems"]]:
                gem_synergies[synergy_type] = synergy_data
                
        if not gem_synergies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No synergies found for gem {gem_name}"
            )
            
        return convert_synergies_to_pascal_case(gem_synergies)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting synergies for gem {gem_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{gem_name}/progression")
async def get_gem_progression(
    gem_name: str,
    data_manager: GameDataManager = Depends(get_data_manager)
) -> dict:
    """Get progression data for a specific gem.

    Args:
        gem_name: Name of the gem to retrieve progression data for
        data_manager: Game data manager instance

    Returns:
        Gem progression data if found

    Raises:
        HTTPException: If gem or progression data is not found
    """
    try:
        logger.info(f"Getting progression data for gem: {gem_name}")
        
        # Load gems data
        gems_file = data_manager.base_path / "gems" / "gems.json"
        if not gems_file.exists():
            raise FileNotFoundError(f"Gems data file not found: {gems_file}")
            
        with open(gems_file) as f:
            progression_data = json.load(f)
            
        # Find the gem
        actual_key = next(
            (k for k in progression_data.keys() if k.lower() == gem_name.lower()),
            None
        )
        if not actual_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gem {gem_name} not found"
            )
            
        gem_data = progression_data[actual_key]
        
        return {
            "Stars": gem_data["stars"],
            "Ranks": gem_data["ranks"],
            "MaxRank": 10,
            "MaxEffect": gem_data["ranks"]["10"]["effects"][0]["text"]
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progression data for gem {gem_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
