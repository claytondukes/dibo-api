"""
Game data manager implementation.

This module provides the core functionality for loading and managing game data,
with support for caching and version-aware loading.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Type

from .schemas import (
    GameDataMetadata,
    GameDataCache,
    GemData,
    EquipmentSets,
    GameStats
)

T = TypeVar("T")
logger = logging.getLogger(__name__)


class GameDataManager:
    """Manages access to indexed game data with caching and version awareness."""

    CATEGORY_LOADERS = {
        "gems": (GemData, "gems/gem_skillmap.json"),
        "equipment_sets": (EquipmentSets, "equipment/sets.json"),
        "stats": (GameStats, "stats.json"),
    }

    def __init__(self, data_dir: Path) -> None:
        """Initialize the game data manager.

        Args:
            data_dir: Path to the indexed data directory
        """
        logger.info(f"Initializing GameDataManager with data_dir: {data_dir}")
        self.data_dir = data_dir
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
        metadata_path = self.data_dir / "metadata.json"
        logger.info(f"Loading metadata from: {metadata_path}")
        with metadata_path.open() as f:
            metadata = json.load(f)
            logger.info(f"Loaded metadata: {metadata}")
            return GameDataMetadata.model_validate(metadata)

    async def get_data(self, category: str) -> Any:
        """Get data for a specific category, reloading if necessary.

        Args:
            category: The data category to retrieve

        Returns:
            The requested data for the category

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

    def _load_json_file(self, rel_path: str) -> Dict:
        """Load a JSON file from the data directory.

        Args:
            rel_path: Relative path to the JSON file from data directory

        Returns:
            Dict: Loaded JSON data
        """
        file_path = self.data_dir / rel_path
        logger.info(f"Loading JSON file from: {file_path}")
        with file_path.open() as f:
            data = json.load(f)
            logger.info(f"Loaded JSON data: {data}")
            return data

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
            logger.info(f"Validating data with model {model.__name__}: {json.dumps(data, indent=2)}")
            validated_data = model.model_validate(data)
            logger.info(f"Successfully validated data for {model.__name__}")
            return validated_data
        except Exception as e:
            logger.error(f"Error validating data for {model.__name__}: {e}")
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
