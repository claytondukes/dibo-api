"""
Unit tests for game data schema models.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from api.models.game_data.schemas import (
    GameDataMetadata,
    Gem,
    GemsBySkill,
    GemSkillMap,
    EquipmentSet,
    EquipmentSets,
    StatValue,
    StatSource,
    GameStats
)


class TestGameDataMetadata:
    """Tests for GameDataMetadata schema."""

    def test_valid_metadata(self, sample_metadata):
        """Test creating metadata with valid data."""
        metadata = GameDataMetadata.model_validate(sample_metadata)
        assert isinstance(metadata.last_updated, datetime)
        assert metadata.version == "1.0"
        assert metadata.data_structure_version == "1.0"

    def test_invalid_metadata_missing_field(self):
        """Test metadata validation with missing required field."""
        invalid_data = {
            "version": "1.0",
            # missing last_updated
            "data_structure_version": "1.0"
        }
        with pytest.raises(ValidationError):
            GameDataMetadata.model_validate(invalid_data)


class TestGem:
    """Tests for Gem schema."""

    def test_valid_gem(self, sample_gem):
        """Test creating a gem with valid data."""
        gem = Gem.model_validate(sample_gem)
        assert gem.stars == "5"
        assert gem.model_dump().get("name") == "Blood-Soaked Jade"

    def test_invalid_stars(self, sample_gem):
        """Test gem validation with invalid star rating."""
        invalid_gem = sample_gem.copy()
        invalid_gem["Stars"] = "3"
        with pytest.raises(ValidationError):
            Gem.model_validate(invalid_gem)

    def test_quality_validation(self, sample_gem):
        """Test quality validation with different star ratings."""
        # Test with 2-star gem
        two_star_gem = sample_gem.copy()
        two_star_gem["Stars"] = "2"
        gem = Gem.model_validate(two_star_gem)
        assert gem.stars == "2"


class TestGemSkillMap:
    """Tests for GemSkillMap schema."""

    def test_valid_gems_data(self, sample_gems_data):
        """Test creating gems data with valid structure."""
        data = GemSkillMap.model_validate(sample_gems_data)
        assert len(data.gems_by_skill.movement) == 1
        assert data.gems_by_skill.movement[0] == "Blood-Soaked Jade"

    def test_empty_categories(self):
        """Test gems data with empty skill categories."""
        data = GemSkillMap(gems_by_skill=GemsBySkill())
        assert len(data.gems_by_skill.movement) == 0
        assert len(data.gems_by_skill.primary_attack) == 0


class TestEquipmentSet:
    """Tests for the EquipmentSet model."""

    def test_valid_set(self, sample_equipment_set):
        """Test creating an equipment set with valid data."""
        set_data = EquipmentSet.model_validate(sample_equipment_set)
        assert set_data.pieces == 6
        assert set_data.bonuses.two == "Increases DoT damage by 15%"
        assert set_data.bonuses.four == "Additional DoT damage"
        assert set_data.bonuses.six == "Unleash lightning strikes"

    def test_missing_bonus(self, sample_equipment_set):
        """Test validation with missing optional bonuses."""
        set_data = sample_equipment_set.copy()
        del set_data["bonuses"]["6"]
        set_data = EquipmentSet.model_validate(set_data)
        assert set_data.bonuses.six is None


class TestEquipmentSets:
    """Tests for the EquipmentSets model."""

    def test_valid_sets_data(self, sample_equipment_sets_data):
        """Test creating EquipmentSets with valid data."""
        sets_data = EquipmentSets.model_validate(sample_equipment_sets_data)
        assert len(sets_data.registry) > 0


class TestStatValue:
    """Tests for the StatValue model."""

    def test_valid_stat_value(self, sample_stat_value):
        """Test creating a stat value with valid data."""
        stat_value = StatValue.model_validate(sample_stat_value)
        assert stat_value.value is not None
        assert stat_value.unit is not None


class TestStatSource:
    """Tests for the StatSource model."""

    def test_valid_stat_source(self, sample_stat_source):
        """Test creating a stat source with valid data."""
        stat_source = StatSource.model_validate(sample_stat_source)
        assert stat_source.name is not None
        assert len(stat_source.base_values) > 0


class TestGameStats:
    """Tests for the GameStats model."""

    def test_valid_stats_data(self, sample_stats_data):
        """Test creating GameStats with valid data."""
        stats_data = GameStats.model_validate(sample_stats_data)
        assert len(stats_data.critical_hit_chance.gems) > 0
