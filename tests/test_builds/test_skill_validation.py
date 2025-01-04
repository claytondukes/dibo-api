"""Tests for skill validation functionality."""

import pytest
from fastapi import HTTPException
from pathlib import Path

from api.builds.service import BuildService


def test_validate_skill_exists(test_data_dir: Path) -> None:
    """Test validation of skill existence in class registry.
    
    This test verifies:
    1. Valid skills are found in the class registry
    2. Invalid skills return appropriate errors
    3. Skills are properly loaded from the indexed data structure
    """
    # Initialize service with test data
    build_service = BuildService(data_dir=test_data_dir)
    
    # Test valid skill combination
    valid_skills = ["Frenzy", "Cleave", "Ground_Stomp", "Leap", "Cleave"]
    assert build_service._validate_skill_selection(valid_skills, "barbarian") is True
    
    # Test missing weapon skill
    invalid_skills = ["Cleave", "Ground_Stomp", "Leap", "Cleave", "Cleave"]
    assert build_service._validate_skill_selection(invalid_skills, "barbarian") is False
    
    # Test wrong number of skills
    too_few_skills = ["Frenzy", "Cleave", "Ground_Stomp"]
    assert build_service._validate_skill_selection(too_few_skills, "barbarian") is False
    
    # Test nonexistent skill
    invalid_skill = ["Frenzy", "NonexistentSkill", "Ground_Stomp", "Leap", "Cleave"]
    assert build_service._validate_skill_selection(invalid_skill, "barbarian") is False
    
    # Test invalid class
    assert build_service._validate_skill_selection(valid_skills, "invalid_class") is False
