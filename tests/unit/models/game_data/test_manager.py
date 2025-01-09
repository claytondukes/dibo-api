"""
Unit tests for GameDataManager.
"""

import pytest
from datetime import datetime, timedelta

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas import GemSkillMap


class TestGameDataManager:
    """Tests for GameDataManager."""

    @pytest.fixture
    def manager(self, mock_data_dir):
        """Create a GameDataManager instance with mock data."""
        return GameDataManager(mock_data_dir)

    @pytest.mark.asyncio
    async def test_get_data_invalid_category(self, manager):
        """Test getting data for an invalid category."""
        with pytest.raises(ValueError, match="Unsupported category"):
            await manager.get_data("invalid_category")

    @pytest.mark.asyncio
    async def test_get_gems_data(self, manager):
        """Test getting gems data."""
        data = await manager.get_data("gems")
        assert isinstance(data, GemSkillMap)
        assert len(data.gems_by_skill.movement) == 1
        assert data.gems_by_skill.movement[0] == "Blood-Soaked Jade"

    def test_should_reload_initial(self, manager):
        """Test should_reload returns True for initial load."""
        assert manager._should_reload() is True

    def test_should_reload_after_update(
        self,
        manager,
        mock_data_dir,
        sample_metadata
    ):
        """Test should_reload after data update."""
        # Simulate initial load
        manager._cache.last_loaded = datetime.now()
        
        # Update metadata with newer timestamp
        sample_metadata["last_updated"] = (
            datetime.now() + timedelta(minutes=1)
        ).isoformat()
        
        with open(mock_data_dir / "metadata.json", "w") as f:
            import json
            json.dump(sample_metadata, f)
        
        assert manager._should_reload() is True

    @pytest.mark.asyncio
    async def test_reload_data(self, manager):
        """Test reloading all data."""
        await manager._reload_data()
        assert manager._cache.last_loaded is not None
        assert isinstance(manager._cache.data["gems"], GemSkillMap)
