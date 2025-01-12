"""Tests for class schema models."""

from pathlib import Path
import shutil
from unittest.mock import patch

from api.models.game_data.schemas.classes import (
    ClassListResponse,
    ClassSkill,
    ClassInfo,
    get_available_classes
)


def test_get_available_classes(tmp_path):
    """Test get_available_classes function."""
    # Create test class directories
    classes_dir = tmp_path / "classes"
    classes_dir.mkdir()
    (classes_dir / "barbarian").mkdir()
    (classes_dir / "druid").mkdir()
    
    # Mock settings to use our test directory
    with patch('api.models.game_data.schemas.classes.get_settings') as mock_settings:
        mock_settings.return_value.DATA_DIR = str(tmp_path)
        
        # Test with existing classes
        classes = get_available_classes()
        assert isinstance(classes, list)
        assert all(isinstance(c, str) for c in classes)
        assert sorted(classes) == ["barbarian", "druid"]
        
        # Test with no classes directory
        shutil.rmtree(classes_dir)
        assert get_available_classes() == []


def test_class_list_response():
    """Test ClassListResponse model."""
    response = ClassListResponse(classes=["barbarian", "druid"])
    assert response.classes == ["barbarian", "druid"]


def test_class_skill():
    """Test ClassSkill model."""
    skill = ClassSkill(
        name="Whirlwind",
        description="A spinning attack",
        type="core",
        cooldown=10.0,
        damage_type="physical",
        resource_cost="40 Fury"
    )
    
    assert skill.name == "Whirlwind"
    assert skill.description == "A spinning attack"
    assert skill.type == "core"
    assert skill.cooldown == 10.0
    assert skill.damage_type == "physical"
    assert skill.resource_cost == "40 Fury"
    
    # Test optional fields
    skill = ClassSkill(
        name="Basic Attack",
        description="A basic attack",
        type="basic"
    )
    assert skill.cooldown is None
    assert skill.damage_type is None
    assert skill.resource_cost is None


def test_class_info():
    """Test ClassInfo model."""
    class_info = ClassInfo(
        name="Barbarian",
        description="A mighty warrior",
        primary_resource="Fury",
        mechanics=["Rage Generation", "Berserking"],
        skills={
            "basic": [
                ClassSkill(
                    name="Basic Attack",
                    description="A basic attack",
                    type="basic"
                )
            ],
            "core": [
                ClassSkill(
                    name="Whirlwind",
                    description="A spinning attack",
                    type="core",
                    cooldown=10.0,
                    damage_type="physical",
                    resource_cost="40 Fury"
                )
            ]
        }
    )
    
    assert class_info.name == "Barbarian"
    assert class_info.description == "A mighty warrior"
    assert class_info.primary_resource == "Fury"
    assert class_info.mechanics == ["Rage Generation", "Berserking"]
    assert len(class_info.skills["basic"]) == 1
    assert len(class_info.skills["core"]) == 1
    assert class_info.skills["basic"][0].name == "Basic Attack"
    assert class_info.skills["core"][0].name == "Whirlwind"
    assert class_info.recommended_playstyle is None
    
    # Test with recommended_playstyle
    class_info = ClassInfo(
        name="Barbarian",
        description="A mighty warrior",
        primary_resource="Fury",
        mechanics=["Rage Generation"],
        recommended_playstyle="Aggressive melee combat",
        skills={"basic": [], "core": []}
    )
    assert class_info.recommended_playstyle == "Aggressive melee combat"
