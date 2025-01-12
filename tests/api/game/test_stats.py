"""Tests for stat schema models."""

from api.models.game_data.schemas.stats import (
    StatInfo,
    StatBlock,
    StatCondition,
    StatValue,
    StatSource,
    StatCategory,
    GameStats
)


def test_stat_info():
    """Test StatInfo model."""
    stat = StatInfo(
        name="Attack Speed",
        description="Increases attack speed",
        category="offensive",
        unit="percentage",
        min_value=0.0,
        max_value=100.0,
        sources=["gems", "essences"]
    )
    
    assert stat.name == "Attack Speed"
    assert stat.description == "Increases attack speed"
    assert stat.category == "offensive"
    assert stat.unit == "percentage"
    assert stat.min_value == 0.0
    assert stat.max_value == 100.0
    assert stat.sources == ["gems", "essences"]
    
    # Test optional fields
    stat = StatInfo(
        name="Health",
        description="Maximum health",
        category="defensive",
        sources=[]
    )
    assert stat.unit is None
    assert stat.min_value is None
    assert stat.max_value is None


def test_stat_block():
    """Test StatBlock model."""
    block = StatBlock(
        strength=10,
        dexterity=15,
        intelligence=8,
        vitality=12
    )
    
    assert block.strength == 10
    assert block.dexterity == 15
    assert block.intelligence == 8
    assert block.vitality == 12


def test_stat_condition():
    """Test StatCondition model."""
    condition = StatCondition(
        type="trigger",
        description="On hit",
        cooldown=1.0,
        threshold=0.5
    )
    
    assert condition.type == "trigger"
    assert condition.description == "On hit"
    assert condition.cooldown == 1.0
    assert condition.threshold == 0.5
    
    # Test optional fields
    condition = StatCondition(
        type="state",
        description="While active"
    )
    assert condition.cooldown is None
    assert condition.threshold is None


def test_stat_value():
    """Test StatValue model."""
    value = StatValue(
        value=10.0,
        unit="percentage",
        conditions=[
            StatCondition(
                type="trigger",
                description="On hit"
            )
        ],
        scaling=True,
        min_value=0.0,
        max_value=100.0
    )
    
    assert value.value == 10.0
    assert value.unit == "percentage"
    assert len(value.conditions) == 1
    assert value.scaling is True
    assert value.min_value == 0.0
    assert value.max_value == 100.0
    
    # Test optional fields
    value = StatValue(value=5.0)
    assert value.unit is None
    assert value.conditions == []
    assert value.scaling is None
    assert value.min_value is None
    assert value.max_value is None


def test_stat_source():
    """Test StatSource model."""
    source = StatSource(
        name="Ruby Gem",
        stars=5,
        base_values=[
            StatValue(value=10.0, unit="percentage")
        ],
        rank_10_values=[
            StatValue(value=20.0, unit="percentage")
        ],
        conditions=[
            StatCondition(type="trigger", description="On hit")
        ],
        rank_10_conditions=[
            StatCondition(type="trigger", description="On critical hit")
        ]
    )
    
    assert source.name == "Ruby Gem"
    assert source.stars == 5
    assert len(source.base_values) == 1
    assert len(source.rank_10_values) == 1
    assert len(source.conditions) == 1
    assert len(source.rank_10_conditions) == 1


def test_stat_category():
    """Test StatCategory model."""
    category = StatCategory(
        gems=[
            StatSource(
                name="Ruby Gem",
                stars=5,
                base_values=[StatValue(value=10.0)]
            )
        ],
        essences=[
            StatSource(
                name="Fire Essence",
                base_values=[StatValue(value=15.0)]
            )
        ],
        skills=[{"name": "Fireball", "value": 20.0}],
        description="Stats affecting attack speed"
    )
    
    assert len(category.gems) == 1
    assert len(category.essences) == 1
    assert len(category.skills) == 1
    assert category.description == "Stats affecting attack speed"


def test_game_stats():
    """Test GameStats model."""
    stats = GameStats(
        critical_hit_chance=StatCategory(
            gems=[
                StatSource(
                    name="Ruby Gem",
                    stars=5,
                    base_values=[StatValue(value=10.0)]
                )
            ]
        ),
        damage_increase=StatCategory(
            essences=[
                StatSource(
                    name="Fire Essence",
                    base_values=[StatValue(value=15.0)]
                )
            ]
        ),
        attack_speed=StatCategory(
            skills=[{"name": "Swift Strike", "value": 20.0}]
        )
    )
    
    assert isinstance(stats.critical_hit_chance, StatCategory)
    assert isinstance(stats.damage_increase, StatCategory)
    assert isinstance(stats.attack_speed, StatCategory)
    assert isinstance(stats.movement_speed, StatCategory)
    assert isinstance(stats.life, StatCategory)
