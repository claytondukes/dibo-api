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
    GemData,
    EquipmentSet,
    EquipmentSets
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
        assert gem.stars == 5
        assert gem.name == "Blood-Soaked Jade"
        assert gem.quality == 5

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
        two_star_gem["Stars"] = 2
        gem = Gem.model_validate(two_star_gem)
        assert gem.stars == 2
        assert isinstance(gem.quality, int), "Quality should be converted to int"


class TestGemData:
    """Tests for GemData schema."""

    def test_valid_gems_data(self, sample_gems_data):
        """Test creating gems data with valid structure."""
        data = GemData.model_validate(sample_gems_data)
        assert len(data.gems_by_skill.movement) == 1
        assert isinstance(data.gems_by_skill.movement[0], Gem)

    def test_empty_categories(self):
        """Test gems data with empty skill categories."""
        data = GemData(gems_by_skill=GemsBySkill())
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
        set_model = EquipmentSet.model_validate(set_data)
        assert set_model.bonuses.six is None


class TestEquipmentSets:
    """Tests for the EquipmentSets model."""

    def test_valid_sets_data(self, sample_equipment_sets_data):
        """Test creating EquipmentSets with valid data."""
        sets = EquipmentSets.model_validate(sample_equipment_sets_data)
        assert sets.metadata.bonus_thresholds == [2, 4, 6]
        assert "Grace of the Flagellant" in sets.registry
        assert sets.registry["Grace of the Flagellant"].pieces == 6
