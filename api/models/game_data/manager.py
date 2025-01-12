"""
Game data manager implementation.

This module provides the core functionality for loading and managing game data,
with support for caching and version-aware loading.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, TypeVar, Type, Union, List, Optional

from pydantic import BaseModel

from api.core.config import Settings, get_settings
from .schemas import (
    BuildTypes,
    GameConstraints,
    SetBonusRegistry,  # Renamed from EquipmentSets
    GemRegistry,
    GemSkillMap,
    GameStats,
    GameSynergies,
    GameDataMetadata,
    GameDataCache,
)
from .schemas.essences import ClassEssences, EssenceData

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class GameDataManager:
    """Manages access to indexed game data with caching and version awareness."""

    CATEGORY_LOADERS = {
        "build_types": (BuildTypes, "build_types.json"),
        "constraints": (GameConstraints, "constraints.json"),
        "sets": (SetBonusRegistry, "sets.json"),  # Renamed from equipment_sets
        "gems/data": (GemRegistry, "gems/gems.json"),
        "gems/skillmap": (GemSkillMap, "gems/gem_skillmap.json"),
        "gems/stat_boosts": (GameStats, "gems/stat_boosts.json"),
        "gems/synergies": (GameSynergies, "gems/synergies.json"),
    }

    # Static gear slots (right side of character)
    GEAR_SLOTS = {
        "HEAD": "Head",           # Helm slot
        "CHEST": "Chest",        # Torso armor
        "SHOULDERS": "Shoulders", # Shoulder armor
        "LEGS": "Legs",          # Leg armor
        "MAIN_HAND_1": "Main Hand (Set 1)",  # Primary weapon set 1
        "OFF_HAND_1": "Off-Hand (Set 1)",    # Off-hand weapon/shield set 1
        "MAIN_HAND_2": "Main Hand (Set 2)",  # Primary weapon set 2
        "OFF_HAND_2": "Off-Hand (Set 2)"     # Off-hand weapon/shield set 2
    }
    
    # Static set slots (left side of character)
    SET_SLOTS = {
        "NECK": "Neck",       # Necklace slot
        "WAIST": "Waist",     # Belt slot
        "HANDS": "Hands",     # Glove slot
        "FEET": "Feet",       # Boot slot
        "RING_1": "Ring 1",   # First ring slot
        "RING_2": "Ring 2",   # Second ring slot
        "BRACER_1": "Bracer 1", # First bracer slot
        "BRACER_2": "Bracer 2"  # Second bracer slot
    }

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the game data manager.

        Args:
            settings: Optional Settings instance. If not provided, will use default settings.
        """
        self.settings = settings or get_settings()
        logger.info(f"Initializing GameDataManager with data_dir: {self.settings.data_path}")
        self._cache = GameDataCache(
            metadata=self._load_metadata(),
            data={},
            last_loaded=None
        )
        self._essence_cache: Dict[str, ClassEssences] = {}

    def _load_metadata(self) -> GameDataMetadata:
        """Load metadata from the indexed data directory.

        Returns:
            GameDataMetadata: Current metadata for the indexed data
        """
        metadata_path = self.settings.data_path / "metadata.json"
        logger.info(f"Loading metadata from: {metadata_path}")
        with metadata_path.open() as f:
            metadata = json.load(f)
            logger.info(f"Loaded metadata: {metadata}")
            return GameDataMetadata.model_validate(metadata)

    def _load_json_file(self, rel_path: str) -> Dict:
        """Load a JSON file from the data directory.

        Args:
            rel_path: Relative path to the JSON file from data directory

        Returns:
            Dict: Loaded JSON data
        """
        file_path = self.settings.data_path / rel_path
        logger.info(f"Loading JSON file from: {file_path}")
        with file_path.open() as f:
            data = json.load(f)
            logger.info(f"Loaded JSON data: {data}")
            return data

    async def get_data(self, category: str) -> Union[BuildTypes, GameConstraints, SetBonusRegistry, 
                                                    GemRegistry, GemSkillMap, GameStats, GameSynergies]:
        """Get data for a specific category, reloading if necessary.

        Args:
            category: The data category to retrieve

        Returns:
            The requested data for the category, properly typed based on the category

        Raises:
            ValueError: If the category is not supported
        """
        logger.info(f"Getting data for category: {category}")
        if category not in self.CATEGORY_LOADERS:
            logger.error(f"Unsupported category: {category}")
            raise ValueError(f"Unsupported category: {category}")

        try:
            if self._should_reload():
                logger.info("Data needs to be reloaded")
                await self._reload_data()
            return self._cache.data.get(category)
        except Exception as e:
            logger.error(f"Error getting data for category {category}: {e}")
            raise ValueError(f"Failed to get data for category {category}: {e}") from e

    def _should_reload(self) -> bool:
        """Check if data needs to be reloaded."""
        if not self._cache or not self._cache.data:
            logger.info("Cache has never been loaded")
            return True
        
        # Check if cache is stale
        if not self._cache.last_loaded:
            logger.info("Cache has never been loaded")
            return True
        
        # Check if metadata has changed
        try:
            metadata = self._load_metadata()
            if metadata.last_updated > self._cache.metadata.last_updated:
                logger.info("Metadata has changed, reloading data")
                return True
        except Exception as e:
            logger.error(f"Error checking metadata: {e}")
            return True
        
        return False

    async def _load_category(
        self,
        category: str,
        model_cls: Type[T],
        file_path: str
    ) -> T:
        """Load a category of game data.

        Args:
            category: The category name
            model_cls: The model class to validate the data with
            file_path: Relative path to the data file

        Returns:
            The loaded and validated data
        """
        logger.info(f"Loading category: {category}")
        logger.info(f"Loading category with model {model_cls.__name__} from {file_path}")
        
        try:
            data = self._load_json_file(file_path)
            logger.info(f"Loaded JSON data: {data}")
            
            logger.info(f"Validating data with model {model_cls.__name__}")
            validated_data = model_cls.model_validate(data)
            logger.info(f"Successfully validated data for {model_cls.__name__}")
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Error loading category {category}: {e}")
            raise ValueError(f"Failed to load category {category}: {e}") from e

    async def _reload_data(self) -> None:
        """Reload all game data into the cache."""
        logger.info("Reloading all game data")
        for category, (model, path) in self.CATEGORY_LOADERS.items():
            logger.info(f"Loading category: {category}")
            self._cache.data[category] = await self._load_category(category, model, path)

        self._cache.metadata = self._load_metadata()
        self._cache.last_loaded = datetime.now()
        logger.info("Finished reloading data")

    async def get_stat_categories(self) -> List[str]:
        """Get available stat categories.

        Returns:
            List[str]: List of available stat categories
        """
        stats = await self.get_data("gems/stat_boosts")
        categories = set()
        for stat in stats.values():
            if isinstance(stat, dict) and "category" in stat:
                categories.add(stat["category"])
        return sorted(list(categories))

    async def get_stat_boosts(self) -> Dict[str, dict]:
        """Get stat boost data with categories.

        Returns:
            Dict[str, dict]: Stat boost data with categories
        """
        try:
            stats = await self.get_data("gems/stat_boosts")
            if not stats:
                logger.error("Failed to get stat boosts data")
                raise ValueError("Failed to get stat boosts data")
            return stats
        except Exception as e:
            logger.error(f"Error getting stat boosts: {e}")
            raise ValueError(f"Failed to get stat boosts: {e}") from e

    async def get_equipment_sets(self) -> dict[str, dict]:
        """Get equipment set data.

        Returns:
            dict[str, dict]: Equipment set data
        """
        logger.info("Getting equipment sets")
        data = await self.get_data("sets")
        return data.model_dump(mode='json') if data else {}

    def get_class_essences(
        self,
        class_name: str,
        slot: Optional[str] = None,
        skill: Optional[str] = None
    ) -> Dict[str, EssenceData]:
        """Get essences for a specific class.

        Args:
            class_name: Name of the class
            slot: Optional gear slot to filter by
            skill: Optional skill name to filter by

        Returns:
            Dict[str, EssenceData]: Dictionary of essence data

        Raises:
            ValueError: If the class is not found or essence data is invalid
        """
        logger.info(f"Getting essences for class: {class_name}")
        try:
            # Check if we have the essences in cache
            if class_name not in self._essence_cache:
                # Load essences from file
                essence_path = self.settings.data_path / "classes" / class_name / "essences.json"
                if not essence_path.exists():
                    logger.error(f"Essence file not found for class {class_name}")
                    raise ValueError(f"No essences found for class {class_name}")

                with essence_path.open() as f:
                    essence_data = json.load(f)
                    self._essence_cache[class_name] = ClassEssences.model_validate(essence_data)

            essences = self._essence_cache[class_name].essences

            # Apply filters
            if slot:
                essences = {
                    k: v for k, v in essences.items()
                    if v.gear_slot.lower() == slot.lower()
                }

            if skill:
                essences = {
                    k: v for k, v in essences.items()
                    if v.modifies_skill.lower() == skill.lower()
                }

            return essences

        except Exception as e:
            logger.error(f"Error getting essences for class {class_name}: {e}")
            raise ValueError(f"Failed to get essences for class {class_name}: {e}") from e
