"""
Game data manager implementation.

This module provides the core functionality for loading and managing game data,
with support for caching and version-aware loading.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Type

from .schemas import (
    GameDataMetadata,
    GameDataCache,
    GemData
)

T = TypeVar("T")


class GameDataManager:
    """Manages access to indexed game data with caching and version awareness."""

    CATEGORY_LOADERS = {
        "gems": (GemData, "gems/gems.json"),
    }

    def __init__(self, data_dir: Path) -> None:
        """Initialize the game data manager.

        Args:
            data_dir: Path to the indexed data directory
        """
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
        with metadata_path.open() as f:
            return GameDataMetadata.model_validate(json.load(f))

    async def get_data(self, category: str) -> Any:
        """Get data for a specific category, reloading if necessary.

        Args:
            category: The data category to retrieve

        Returns:
            The requested data for the category

        Raises:
            ValueError: If the category is not supported
        """
        if category not in self.CATEGORY_LOADERS:
            raise ValueError(f"Unsupported category: {category}")

        if self._should_reload():
            await self._reload_data()
        return self._cache.data.get(category)

    def _should_reload(self) -> bool:
        """Check if the data should be reloaded.

        Returns:
            bool: True if data should be reloaded, False otherwise
        """
        if not self._cache.last_loaded:
            return True

        current_metadata = self._load_metadata()
        return current_metadata.last_updated > self._cache.last_loaded

    def _load_json_file(self, rel_path: str) -> Dict:
        """Load a JSON file from the data directory.

        Args:
            rel_path: Relative path to the JSON file from data directory

        Returns:
            Dict: Loaded JSON data
        """
        file_path = self.data_dir / rel_path
        with file_path.open() as f:
            return json.load(f)

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
        data = self._load_json_file(rel_path)
        return model.model_validate(data)

    async def _reload_data(self) -> None:
        """Reload all game data into the cache."""
        for category, (model, path) in self.CATEGORY_LOADERS.items():
            self._cache.data[category] = self._load_category(model, path)

        self._cache.metadata = self._load_metadata()
        self._cache.last_loaded = datetime.now()
