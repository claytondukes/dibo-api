"""
Game data manager implementation.

This module provides the core functionality for loading and managing game data,
with support for caching and version-aware loading.
"""

import json
import logging
from datetime import datetime
from typing import Dict, TypeVar, Type, Union, List

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

        if self._should_reload():
            logger.info("Data needs to be reloaded")
            await self._reload_data()
        return self._cache.data.get(category)

    def _should_reload(self) -> bool:
        """Check if the data should be reloaded.

        Returns:
            bool: True if data should be reloaded, False otherwise
        """
        if not self._cache.last_loaded:
            logger.info("Cache has never been loaded")
            return True

        current_metadata = self._load_metadata()
        should_reload = current_metadata.last_updated > self._cache.last_loaded
        logger.info(f"Should reload: {should_reload}")
        return should_reload

    def _load_category(
        self,
        model: Type[T],
        rel_path: str
    ) -> T:
        """Load and validate data for a category.

        Args:
            model: Pydantic model class for the category
            rel_path: Relative path to the data file

        Returns:
            Validated model instance
        """
        logger.info(f"Loading category with model {model.__name__} from {rel_path}")
        data = self._load_json_file(rel_path)
        try:
            logger.info(f"Validating data with model {model.__name__}")
            validated_data = model.model_validate(
                data,
                strict=False,  # Allow coercion of values
                from_attributes=True,  # Allow object conversion
            )
            logger.info(f"Successfully validated data for {model.__name__}")
            return validated_data
        except Exception as e:
            # Log the full error details
            logger.error(f"Error validating data for {model.__name__}:")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Data sample: {str(data)[:1000]}")  # First 1000 chars
            raise

    async def _reload_data(self) -> None:
        """Reload all game data into the cache."""
        logger.info("Reloading all game data")
        for category, (model, path) in self.CATEGORY_LOADERS.items():
            logger.info(f"Loading category: {category}")
            self._cache.data[category] = self._load_category(model, path)

        self._cache.metadata = self._load_metadata()
        self._cache.last_loaded = datetime.now()
        logger.info("Finished reloading data")

    async def get_stat_categories(self) -> List[str]:
        """Get available stat categories.

        Returns:
            List[str]: List of available stat categories
        """
        stats = await self.get_stat_boosts()
        categories = set()
        for stat in stats.values():
            if isinstance(stat, dict) and "category" in stat:
                categories.add(stat["category"])
        return sorted(list(categories))

    async def get_stat_boosts(self) -> Dict[str, dict[str, Union[str, List[str]]]]:
        """Get stat boost data with categories.

        Returns:
            Dict[str, dict[str, Union[str, List[str]]]]: Stat boost data with categories
        """
        logger.info("Getting stat boosts")
        data = await self.get_data("gems/stat_boosts")
        if not data:
            return {}
        
        # Convert to dict using Pydantic v2's model_dump
        data_dict = data.model_dump(mode='json')
        
        stats: Dict[str, dict[str, Union[str, List[str]]]] = {}
        for stat_name, stat_data in data_dict.items():
            # Skip metadata fields
            if stat_name == "metadata":
                continue
                
            # Determine category based on stat effects
            category = "utility"  # Default category
            if any(term in stat_name for term in ["damage", "critical", "attack"]):
                category = "offensive"
            elif any(term in stat_name for term in ["life", "armor", "resistance", "defense"]):
                category = "defensive"
            
            # Add category and other metadata
            stats[stat_name] = {
                "name": stat_name,
                "description": stat_data.get("description", f"Increases {stat_name.replace('_', ' ')}"),
                "category": category,
                "gems": stat_data.get("gems", []),
                "unit": "percentage"  # Most stats are percentages
            }
        
        return stats

    async def get_equipment_sets(self) -> dict[str, dict]:
        """Get equipment set data.

        Returns:
            dict[str, dict]: Equipment set data
        """
        logger.info("Getting equipment sets")
        data = await self.get_data("sets")
        return data.model_dump(mode='json') if data else {}
