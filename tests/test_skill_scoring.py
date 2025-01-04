"""Tests for skill scoring functionality.

TODO: This file will be consolidated into test_builds/test_skill_selection.py
Keep for now as it contains useful test data setup patterns, particularly
the comprehensive test data directory structure.
"""

import json
import pytest
from pathlib import Path

from api.builds.models import BuildType, BuildFocus, Gem
from api.builds.service import BuildService


@pytest.fixture
def test_data_dir(tmp_path):
    """Create test data directory with minimal required data."""
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)
    
    # Create subdirectories
    class_dir = data_dir / "classes" / "barbarian"
    gem_dir = data_dir / "gems"
    equipment_dir = data_dir / "equipment"
    class_dir.mkdir(parents=True)
    gem_dir.mkdir(parents=True)
    equipment_dir.mkdir(parents=True)
    
    # Core data files
    constraints = {
        "gem_slots": {"min": 1, "max": 3},
        "essence_slots": {"min": 1, "max": 3}
    }
    with open(data_dir / "constraints.json", "w") as f:
        json.dump(constraints, f)
        
    synergies = {
        "damage_boost": {
            "gems": ["Berserker's Eye"],
            "essences": [],
            "skills": ["Cleave"],
            "conditions": {}
        }
    }
    with open(data_dir / "synergies.json", "w") as f:
        json.dump(synergies, f)
    with open(gem_dir / "synergies.json", "w") as f:
        json.dump(synergies, f)
        
    stats = {
        "base": {
            "health": 100,
            "damage": 10
        }
    }
    with open(data_dir / "stats.json", "w") as f:
        json.dump(stats, f)
    
    # Gem data files
    progression = {
        "Berserker's Eye": {
            "levels": {
                "1": {"power": 10},
                "2": {"power": 20}
            }
        }
    }
    with open(gem_dir / "progression.json", "w") as f:
        json.dump(progression, f)
        
    stat_boosts = {}
    with open(gem_dir / "stat_boosts.json", "w") as f:
        json.dump(stat_boosts, f)
        
    gems = {
        "Berserker's Eye": {
            "name": "Berserker's Eye",
            "type": "damage",
            "description": "Increases damage"
        }
    }
    with open(gem_dir / "gems.json", "w") as f:
        json.dump(gems, f)
        
    # Class data files
    base_skills = {
        "registry": {
            "Cleave": {
                "base_type": "damage",
                "second_base_type": None,
                "cooldown": "medium"
            }
        }
    }
    with open(class_dir / "base_skills.json", "w") as f:
        json.dump(base_skills, f)
        
    essences = {}
    with open(class_dir / "essences.json", "w") as f:
        json.dump(essences, f)
        
    constraints = {
        "skill_slots": {"min": 1, "max": 6}
    }
    with open(class_dir / "constraints.json", "w") as f:
        json.dump(constraints, f)
        
    # Equipment data files
    sets = {}
    with open(equipment_dir / "sets.json", "w") as f:
        json.dump(sets, f)
        
    return data_dir


def test_skill_score_gem_synergies(test_data_dir):
    """Test that gem synergies are properly scored for skills.
    
    This test verifies that a skill with a matching gem synergy scores
    higher than the same skill without the synergistic gem.
    """
    # Initialize service with test data path
    service = BuildService(data_dir=test_data_dir)
    
    # Test skill with gem synergy
    gems = [Gem(name="Berserker's Eye", rank=1)]
    synergy_score = service._calculate_skill_score(
        "Cleave",
        BuildType.RAID,
        BuildFocus.DPS,
        gems
    )
    
    # Test same skill without gem synergy
    no_synergy_score = service._calculate_skill_score(
        "Cleave",
        BuildType.RAID,
        BuildFocus.DPS,
        []
    )
    
    # The score with the gem should be higher due to synergy
    assert synergy_score > no_synergy_score, (
        f"Expected score with Berserker's Eye ({synergy_score}) to be higher than "
        f"score without gem ({no_synergy_score}) for Cleave"
    )
