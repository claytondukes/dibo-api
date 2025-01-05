"""
Game data management module for the DIBO API.

This module provides a structured way to access and manage game data stored in the
indexed data directory, with support for versioning and caching.
"""

from .manager import GameDataManager
from .schemas import GameDataMetadata

__all__ = ["GameDataManager", "GameDataMetadata"]
