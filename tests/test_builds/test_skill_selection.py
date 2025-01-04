"""Test skill selection logic."""

import json
import pytest
from fastapi import HTTPException
from typing import Dict, List

from api.builds.models import BuildFocus, BuildType, Gem, Skill
from api.builds.service import BuildService


def create_test_skill(base_type: str, cooldown: str = "medium", tags: List[str] = None, 
                     second_base_type: str = None) -> Dict:
    """Create a test skill with given parameters."""
    skill = {
        "base_type": base_type,
        "cooldown": cooldown,
        "tags": tags or []
    }
    if second_base_type:
        skill["second_base_type"] = second_base_type
    return skill

def create_test_essence(effect: str, effect_tags: List[str], skill_type: str) -> Dict:
    """Create a test essence with given parameters."""
    return {
        "effect": effect,
        "effect_tags": effect_tags,
        "skill_type": skill_type
    }

@pytest.fixture
def mock_skill_data():
    """Mock skill data for testing."""
    return {
        "registry": {
            "Cleave": create_test_skill("damage", "short", ["melee", "aoe"]),
            "Ground_Stomp": create_test_skill("control", "medium", ["control", "stun"]),
            "War_Cry": create_test_skill("buff", "long", ["buff", "aoe"]),
            "Sprint": create_test_skill("buff", "short", ["movement", "speed"], "mobility"),
            "Whirlwind": create_test_skill("damage", "medium", ["aoe"])
        }
    }


@pytest.fixture
def mock_essence_data():
    """Mock essence data for testing."""
    return {
        "metadata": {
            "version": "1.0",
            "class": "barbarian"
        },
        "essences": {
            "cleave_bleed": create_test_essence(
                "Cleave deals 30% increased damage",
                ["damage", "bleed"],
                "damage"
            ),
            "cleave_stun": create_test_essence(
                "Cleave has a 20% chance to stun enemies",
                ["control"],
                "damage"
            ),
            "stomp_range": create_test_essence(
                "Ground Stomp range increased by 50%",
                ["utility"],
                "control"
            ),
            "stomp_damage": create_test_essence(
                "Ground Stomp deals 30% more damage",
                ["damage"],
                "control"
            ),
            "cry_duration": create_test_essence(
                "War Cry duration increased by 20%",
                ["buff", "duration"],
                "buff"
            ),
            "sprint_damage": create_test_essence(
                "Sprint increases damage by 20%",
                ["damage"],
                "buff"
            ),
            "whirl_speed": create_test_essence(
                "Whirlwind attack speed increased by 25%",
                ["damage", "attack_speed"],
                "damage"
            ),
            "whirl_crit": create_test_essence(
                "Whirlwind cooldown reduced by 2 seconds",
                ["cooldown"],
                "damage"
            )
        },
        "indexes": {
            "by_skill": {
                "Cleave": ["cleave_bleed", "cleave_stun"],
                "Ground_Stomp": ["stomp_range", "stomp_damage"],
                "War_Cry": ["cry_duration"],
                "Sprint": ["sprint_damage"],
                "Whirlwind": ["whirl_speed", "whirl_crit"]
            },
            "by_tag": {
                "damage": ["cleave_bleed", "stomp_damage", "sprint_damage", "whirl_speed"],
                "dot": ["cleave_bleed"],
                "control": ["cleave_stun"],
                "utility": ["stomp_range", "cry_duration"],
                "attack_speed": ["whirl_speed"],
                "cooldown": ["whirl_crit"]
            },
            "by_slot": {
                "slot1": ["cleave_bleed", "stomp_range", "whirl_speed"],
                "slot2": ["cleave_stun", "stomp_damage", "whirl_crit"],
                "slot3": ["cry_duration", "sprint_damage"]
            }
        }
    }


@pytest.fixture
def mock_constraints():
    """Mock constraints for testing."""
    return {
        "max_skills": 4,
        "required_types": {
            "control_or_buff": 1,
            "damage": 1
        },
        "gem_slots": 3,
        "essence_slots": 2
    }


@pytest.fixture
def mock_synergies():
    """Mock synergy data for testing."""
    return {
        "control": {
            "gems": ["Control Gem"],
            "essences": ["stomp_range", "stomp_damage"],
            "skills": ["Ground_Stomp"]
        },
        "critical_hit": {
            "gems": ["Berserker's Eye"],
            "essences": ["cleave_bleed", "cleave_stun"],
            "skills": ["Cleave", "Whirlwind"]
        },
        "movement": {
            "gems": ["Swift Gem"],
            "essences": ["sprint_damage"],
            "skills": ["Sprint"]
        }
    }


@pytest.fixture
def mock_stats():
    """Mock stats data for testing."""
    return {
        "base_stats": {
            "health": 100,
            "armor": 10,
            "damage": 20
        },
        "scaling": {
            "health_per_level": 10,
            "armor_per_level": 1,
            "damage_per_level": 2
        }
    }


@pytest.fixture
def mock_gem_data():
    """Mock gem data for testing."""
    return {
        "progression": {
            "Control Gem": {
                "levels": [1, 2, 3],
                "effects": ["20% control duration", "30% control duration", "40% control duration"]
            },
            "Berserker's Eye": {
                "levels": [1, 2, 3],
                "effects": ["10% crit chance", "15% crit chance", "20% crit chance"]
            },
            "Swift Gem": {
                "levels": [1, 2, 3],
                "effects": ["10% speed", "15% speed", "20% speed"]
            }
        },
        "stat_boosts": {
            "Control Gem": {"control_duration": 20},
            "Berserker's Eye": {"crit_chance": 10},
            "Swift Gem": {"movement_speed": 10}
        },
        "synergies": {
            "Control Gem": ["Ground_Stomp"],
            "Berserker's Eye": ["Cleave", "Whirlwind"],
            "Swift Gem": ["Sprint"]
        },
        "gems": {
            "Control Gem": {
                "type": "utility",
                "description": "Increases control duration"
            },
            "Berserker's Eye": {
                "type": "damage",
                "description": "Increases critical hit chance"
            },
            "Swift Gem": {
                "type": "utility",
                "description": "Increases movement speed"
            }
        }
    }


@pytest.fixture
def mock_equipment_data():
    """Mock equipment data for testing."""
    return {
        "sets": {
            "Warrior's Set": {
                "pieces": ["Helmet", "Chest", "Gloves"],
                "bonuses": {
                    "2": "20% increased damage",
                    "3": "30% increased armor"
                }
            }
        }
    }


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory with mock data files."""
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
    
    # Equipment data files
    equipment_sets = {
        "Warrior's Set": {
            "pieces": ["Helmet", "Chest", "Gloves"],
            "bonuses": {
                "2": "20% increased damage",
                "3": "30% increased armor"
            }
        }
    }
    with open(equipment_dir / "sets.json", "w") as f:
        json.dump(equipment_sets, f)
    
    # Class data files
    base_skills = {
        "registry": {
            "Cleave": create_test_skill("damage", "short", ["melee", "aoe"]),
            "Ground_Stomp": create_test_skill("control", "medium", ["control", "stun"]),
            "Sprint": create_test_skill("buff", "short", ["movement", "speed"], "mobility"),
            "War_Cry": create_test_skill("buff", "long", ["buff", "aoe"])
        }
    }
    with open(class_dir / "base_skills.json", "w") as f:
        json.dump(base_skills, f)
        
    class_constraints = {
        "min_skills": 3,
        "max_skills": 6,
        "required_types": {
            "damage": 1,
            "control_or_buff": 1,
            "mobility": 1
        }
    }
    with open(class_dir / "constraints.json", "w") as f:
        json.dump(class_constraints, f)
        
    essences = {
        "metadata": {
            "version": "1.0",
            "class": "barbarian"
        },
        "essences": {
            "cleave_bleed": create_test_essence(
                "Cleave deals 30% increased damage",
                ["damage", "bleed"],
                "damage"
            ),
            "stomp_duration": create_test_essence(
                "Ground Stomp stuns for 50% longer",
                ["control", "duration"],
                "control"
            ),
            "cry_duration": create_test_essence(
                "War Cry duration increased by 20%",
                ["buff", "duration"],
                "buff"
            ),
            "stomp_range": create_test_essence(
                "Ground Stomp has increased range",
                ["control", "range"],
                "control"
            ),
            "whirl_speed": create_test_essence(
                "Whirlwind movement speed increased by 30%",
                ["movement", "speed"],
                "mobility"
            ),
            "whirl_crit": create_test_essence(
                "Whirlwind critical strike chance increased",
                ["damage", "critical"],
                "damage"
            )
        },
        "indexes": {
            "by_skill": {
                "Cleave": ["cleave_bleed"],
                "Ground_Stomp": ["stomp_duration", "stomp_range"],
                "War_Cry": ["cry_duration"],
                "Whirlwind": ["whirl_speed", "whirl_crit"]
            },
            "by_type": {
                "damage": ["cleave_bleed", "whirl_crit"],
                "control": ["stomp_duration", "stomp_range"],
                "buff": ["cry_duration"],
                "mobility": ["whirl_speed"]
            },
            "by_slot": {
                "weapon": ["cleave_bleed", "whirl_crit"],
                "armor": ["stomp_duration", "stomp_range"],
                "jewelry": ["cry_duration", "whirl_speed"]
            }
        }
    }
    with open(class_dir / "essences.json", "w") as f:
        json.dump(essences, f)
    
    return data_dir


@pytest.fixture
def mock_build_service(mock_data_dir):
    """Create a BuildService with mock data."""
    return BuildService(data_dir=mock_data_dir)


def test_skill_score_dps_focus(mock_build_service):
    """Test skill scoring with DPS focus."""
    # Test damage skill (Cleave)
    score = mock_build_service._calculate_skill_score(
        skill_name="Cleave",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score >= 0.7  # High score for damage skill with DPS focus
    
    # Test control skill (Ground_Stomp)
    score = mock_build_service._calculate_skill_score(
        skill_name="Ground_Stomp",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score <= 0.4  # Lower score for control skill with DPS focus


def test_skill_score_survival_focus(mock_build_service):
    """Test skill scoring with survival focus."""
    # Test buff skill (War_Cry)
    score = mock_build_service._calculate_skill_score(
        skill_name="War_Cry",
        build_type=BuildType.RAID,
        focus=BuildFocus.SURVIVAL,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score >= 0.6  # High score for buff skill with survival focus
    
    # Test damage skill (Whirlwind)
    score = mock_build_service._calculate_skill_score(
        skill_name="Whirlwind",
        build_type=BuildType.RAID,
        focus=BuildFocus.SURVIVAL,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score <= 0.3  # Lower score for damage skill with survival focus


def test_skill_score_build_type_alignment(mock_build_service):
    """Test skill scoring based on build type."""
    # Test control skill in PvP
    score = mock_build_service._calculate_skill_score(
        skill_name="Ground_Stomp",
        build_type=BuildType.PVP,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score >= 0.5  # Higher score for control in PvP
    
    # Test mobility skill in farming
    score = mock_build_service._calculate_skill_score(
        skill_name="Sprint",
        build_type=BuildType.FARM,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score >= 0.5  # Higher score for mobility in farming


def test_skill_score_cooldown_impact(mock_build_service):
    """Test impact of cooldown on skill scoring."""
    # Test short cooldown skill (Sprint - 5s)
    short_cd_score = mock_build_service._calculate_skill_score(
        skill_name="Sprint",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    
    # Test long cooldown skill (War_Cry - 15s)
    long_cd_score = mock_build_service._calculate_skill_score(
        skill_name="War_Cry",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    
    assert short_cd_score > long_cd_score  # Short cooldown should score higher


def test_skill_score_gem_synergies(mock_build_service):
    """Test skill scoring with gem synergies."""
    # Test skill with gem synergy
    gems = [Gem(name="Berserker's Eye", rank=1)]
    synergy_score = mock_build_service._calculate_skill_score(
        skill_name="Cleave",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=gems,
        character_class="barbarian"
    )
    
    # Test same skill without gem synergy
    no_synergy_score = mock_build_service._calculate_skill_score(
        skill_name="Cleave",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    
    assert synergy_score > no_synergy_score  # Gem synergy should increase score


def test_skill_score_invalid_skill(mock_build_service):
    """Test scoring an invalid skill."""
    score = mock_build_service._calculate_skill_score(
        skill_name="NonexistentSkill",
        build_type=BuildType.RAID,
        focus=BuildFocus.DPS,
        selected_gems=[],
        character_class="barbarian"
    )
    assert score == 0.0  # Invalid skills should score 0


def test_validate_skill_selection_basic(mock_build_service):
    """Test basic skill selection validation."""
    # Valid selection with damage and control
    valid_skills = ["Cleave", "Ground_Stomp", "Sprint"]
    assert mock_build_service._validate_skill_selection(
        valid_skills, "barbarian"
    )
    
    # Invalid - no damage skill
    invalid_skills = ["Ground_Stomp", "War_Cry", "Sprint"]
    assert not mock_build_service._validate_skill_selection(
        invalid_skills, "barbarian"
    )
    
    # Invalid - no control/buff skill
    invalid_skills = ["Cleave", "Whirlwind"]
    assert not mock_build_service._validate_skill_selection(
        invalid_skills, "barbarian"
    )


def test_validate_skill_selection_count(mock_build_service):
    """Test skill count validation."""
    # Too many skills
    too_many = ["Cleave", "Ground_Stomp", "War_Cry", "Sprint", "Whirlwind"]
    assert not mock_build_service._validate_skill_selection(
        too_many, "barbarian"
    )
    
    # Empty selection
    assert not mock_build_service._validate_skill_selection(
        [], "barbarian"
    )


def test_validate_skill_selection_cooldowns(mock_build_service):
    """Test cooldown distribution validation."""
    # Too many long cooldowns (War_Cry 15s)
    bad_cooldowns = ["Cleave", "War_Cry", "Ground_Stomp"]
    assert not mock_build_service._validate_skill_selection(
        bad_cooldowns, "barbarian"
    )
    
    # Good cooldown mix (Sprint 5s, Cleave 6s, Ground_Stomp 9s)
    good_cooldowns = ["Sprint", "Cleave", "Ground_Stomp"]
    assert mock_build_service._validate_skill_selection(
        good_cooldowns, "barbarian"
    )


def test_validate_skill_selection_invalid_skills(mock_build_service):
    """Test validation with invalid skills."""
    invalid_skills = ["Cleave", "NonexistentSkill", "Ground_Stomp"]
    assert not mock_build_service._validate_skill_selection(
        invalid_skills, "barbarian"
    )


def test_validate_skill_selection_types(mock_build_service):
    """Test skill type requirements validation."""
    # Valid selection with all required types
    valid_skills = ["Cleave", "Ground_Stomp", "Sprint"]  # damage, control, mobility
    assert mock_build_service._validate_skill_selection(valid_skills, "barbarian")
    
    # Missing damage type
    no_damage = ["Ground_Stomp", "Sprint", "War_Cry"]  # control, mobility, buff
    assert not mock_build_service._validate_skill_selection(no_damage, "barbarian")
    
    # Missing control/buff type
    no_control_buff = ["Cleave", "Cleave", "Furious_Charge"]  # damage, damage, dash
    assert not mock_build_service._validate_skill_selection(no_control_buff, "barbarian")
    
    # Missing mobility type
    no_mobility = ["Cleave", "Ground_Stomp", "War_Cry"]  # damage, control, buff
    assert not mock_build_service._validate_skill_selection(no_mobility, "barbarian")
    
    # Using buff instead of control is valid
    with_buff = ["Cleave", "War_Cry", "Sprint"]  # damage, buff, mobility
    assert mock_build_service._validate_skill_selection(with_buff, "barbarian")


def test_validate_skill_selection_mobility(mock_build_service):
    """Test mobility skill requirement validation."""
    # Valid with mobility base type
    valid_base_type = ["Cleave", "Ground_Stomp", "Sprint"]  # Sprint has mobility base type
    assert mock_build_service._validate_skill_selection(valid_base_type, "barbarian")
    
    # Valid with mobility tag
    mock_build_service.class_data["barbarian"]["base_skills"]["registry"]["Leap"] = create_test_skill(
        "damage", "medium", ["leap", "damage"]  # Mobility through tag
    )
    valid_tag = ["Cleave", "Ground_Stomp", "Leap"]
    assert mock_build_service._validate_skill_selection(valid_tag, "barbarian")
    
    # Valid with charge tag
    mock_build_service.class_data["barbarian"]["base_skills"]["registry"]["Charge"] = create_test_skill(
        "damage", "medium", ["charge", "damage"]  # Mobility through different tag
    )
    valid_charge = ["Cleave", "Ground_Stomp", "Charge"]
    assert mock_build_service._validate_skill_selection(valid_charge, "barbarian")
    
    # Invalid without any mobility
    no_mobility = ["Cleave", "Ground_Stomp", "War_Cry"]
    assert not mock_build_service._validate_skill_selection(no_mobility, "barbarian")
    
    # Invalid with only movement speed (not mobility)
    mock_build_service.class_data["barbarian"]["base_skills"]["registry"]["Swift"] = create_test_skill(
        "buff", "short", ["speed"]  # Speed but not mobility
    )
    speed_only = ["Cleave", "Ground_Stomp", "Swift"]
    assert not mock_build_service._validate_skill_selection(speed_only, "barbarian")


def test_calculate_essence_score_dps_focus(mock_build_service):
    """Test essence scoring with DPS focus."""
    # Test damage essence
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cleave_bleed"],
        BuildType.RAID,
        BuildFocus.DPS,
        []
    )
    assert score >= 0.6  # High score for damage essence with DPS focus
    
    # Test non-damage essence
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cry_duration"],
        BuildType.RAID,
        BuildFocus.DPS,
        []
    )
    assert score <= 0.3  # Lower score for buff essence with DPS focus


def test_calculate_essence_score_survival_focus(mock_build_service):
    """Test essence scoring with survival focus."""
    # Test defensive essence
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cry_duration"],
        BuildType.RAID,
        BuildFocus.SURVIVAL,
        []
    )
    assert score >= 0.6  # High score for buff essence with survival focus
    
    # Test offensive essence
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cleave_bleed"],
        BuildType.RAID,
        BuildFocus.SURVIVAL,
        []
    )
    assert score <= 0.3  # Lower score for damage essence with survival focus


def test_calculate_essence_score_build_type(mock_build_service):
    """Test essence scoring based on build type."""
    # Test PvP essence in PvP build
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["stomp_range"],
        BuildType.PVP,
        BuildFocus.DPS,
        []
    )
    assert score >= 0.5  # Higher score for PvP essence in PvP
    
    # Test PvE essence in PvP build
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cleave_bleed"],
        BuildType.PVP,
        BuildFocus.DPS,
        []
    )
    assert score <= 0.3  # Lower score for PvE essence in PvP


def test_calculate_essence_score_percentage_bonus(mock_build_service):
    """Test essence scoring with percentage bonuses."""
    # Test essence with percentage bonus
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["cleave_bleed"],
        BuildType.RAID,
        BuildFocus.DPS,
        []
    )
    assert score >= 0.4  # Higher score for percentage-based improvement


def test_calculate_essence_score_cooldown_reduction(mock_build_service):
    """Test essence scoring with cooldown reduction."""
    # Test essence with cooldown reduction
    score = mock_build_service._calculate_essence_score(
        mock_build_service.class_data["barbarian"]["essences"]["essences"]["whirl_crit"],
        BuildType.RAID,
        BuildFocus.DPS,
        []
    )
    assert score >= 0.3  # Higher score for cooldown reduction


def test_select_skills_integration(mock_build_service):
    """Integration test for skill selection."""
    # Test DPS-focused PvP build
    selected_skills = mock_build_service._select_skills(
        BuildType.PVP,
        BuildFocus.DPS,
        [Gem(name="Berserker's Eye", rank=1)],
        None,
        "barbarian"
    )
    
    # Verify selection
    skill_names = [s.name for s in selected_skills]
    assert len(selected_skills) <= mock_build_service.class_constraints["barbarian"]["max_skills"]
    assert any(s.name for s in selected_skills if mock_build_service.class_data["barbarian"]["base_skills"]["registry"][s.name]["base_type"] == "damage")
    assert any(s.name for s in selected_skills if mock_build_service.class_data["barbarian"]["base_skills"]["registry"][s.name]["base_type"] in ["control", "buff"])
    assert all(s.essence is not None for s in selected_skills)  # All skills should have essences
    
    # Test survival-focused PvE build
    selected_skills = mock_build_service._select_skills(
        BuildType.RAID,
        BuildFocus.SURVIVAL,
        [],
        None,
        "barbarian"
    )
    
    # Verify selection
    skill_names = [s.name for s in selected_skills]
    assert len(selected_skills) <= mock_build_service.class_constraints["barbarian"]["max_skills"]
    assert any(s.name for s in selected_skills if mock_build_service.class_data["barbarian"]["base_skills"]["registry"][s.name]["base_type"] == "damage")
    assert any(s.name for s in selected_skills if mock_build_service.class_data["barbarian"]["base_skills"]["registry"][s.name]["base_type"] in ["control", "buff"])
    assert all(s.essence is not None for s in selected_skills)  # All skills should have essences


def test_validate_skill_selection_cooldowns_detailed(mock_build_service):
    """Test detailed cooldown validation rules."""
    # Valid with good cooldown distribution
    valid_mix = ["Cleave", "Ground_Stomp", "Sprint"]  # 2 short, 1 medium
    assert mock_build_service._validate_skill_selection(valid_mix, "barbarian")
    
    # Invalid with no short cooldown skills
    all_medium = ["Ground_Stomp", "Ground_Stomp", "Ground_Stomp"]
    assert not mock_build_service._validate_skill_selection(all_medium, "barbarian")
    
    # Invalid with too many long cooldowns
    too_many_long = ["Cleave", "War_Cry", "War_Cry", "War_Cry"]  # 3/4 are long
    assert not mock_build_service._validate_skill_selection(too_many_long, "barbarian")
    
    # Valid with maximum allowed long cooldowns
    max_long = ["Cleave", "Sprint", "War_Cry", "War_Cry", "Ground_Stomp", "Ground_Stomp"]  # 2/6 are long
    assert mock_build_service._validate_skill_selection(max_long, "barbarian")
    
    # Test edge cases
    mock_build_service.class_data["barbarian"]["base_skills"]["registry"].update({
        "Quick": create_test_skill("damage", "short", ["damage"]),
        "Slow": create_test_skill("damage", "long", ["damage"])
    })
    
    # Valid with exactly one-third long cooldowns
    one_third_long = ["Quick", "Quick", "Quick", "Slow", "Slow", "Slow"]  # 3/6 are long
    assert not mock_build_service._validate_skill_selection(one_third_long, "barbarian")
    
    # Invalid with slightly over one-third long cooldowns
    over_one_third = ["Quick", "Quick", "Slow", "Slow", "Slow"]  # 3/5 are long
    assert not mock_build_service._validate_skill_selection(over_one_third, "barbarian")
