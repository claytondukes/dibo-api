"""Tests for synergy schema models."""

from api.models.game_data.schemas.synergies import (
    SynergyCondition,
    SynergyGroup,
    SynergyEffect,
    SynergyTier,
    Synergy,
    GameSynergies
)


def test_synergy_condition():
    """Test SynergyCondition model."""
    condition = SynergyCondition(
        type="trigger",
        state=None,
        trigger="on_hit",
        description="On hit",
        cooldown=1.0,
        threshold=None
    )
    
    assert condition.type == "trigger"
    assert condition.state is None
    assert condition.trigger == "on_hit"
    assert condition.description == "On hit"
    assert condition.cooldown == 1.0
    assert condition.threshold is None
    
    # Test optional fields
    condition = SynergyCondition(
        type="state",
        description="While active"
    )
    assert condition.state is None
    assert condition.trigger is None
    assert condition.cooldown is None
    assert condition.threshold is None


def test_synergy_group():
    """Test SynergyGroup model."""
    group = SynergyGroup(
        gems=["ruby", "sapphire"],
        essences=["fire", "water"],
        skills=["fireball", "ice_bolt"],
        conditions={
            "ruby": [
                SynergyCondition(
                    type="trigger",
                    trigger="on_hit",
                    description="On hit",
                    cooldown=1.0
                )
            ]
        }
    )
    
    assert group.gems == ["ruby", "sapphire"]
    assert group.essences == ["fire", "water"]
    assert group.skills == ["fireball", "ice_bolt"]
    assert len(group.conditions["ruby"]) == 1
    assert group.conditions["ruby"][0].type == "trigger"
    
    # Test empty group
    group = SynergyGroup()
    assert group.gems == []
    assert group.essences == []
    assert group.skills == []
    assert group.conditions == {}


def test_synergy_effect():
    """Test SynergyEffect model."""
    effect = SynergyEffect(
        description="Increases attack speed",
        value=10.0,
        unit="percentage"
    )
    
    assert effect.description == "Increases attack speed"
    assert effect.value == 10.0
    assert effect.unit == "percentage"
    
    # Test without unit
    effect = SynergyEffect(
        description="Adds stun effect",
        value=1.0
    )
    assert effect.unit is None


def test_synergy_tier():
    """Test SynergyTier model."""
    tier = SynergyTier(
        required=3,
        effects=[
            SynergyEffect(
                description="Increases attack speed",
                value=10.0,
                unit="percentage"
            ),
            SynergyEffect(
                description="Adds stun chance",
                value=5.0,
                unit="percentage"
            )
        ]
    )
    
    assert tier.required == 3
    assert len(tier.effects) == 2
    assert tier.effects[0].description == "Increases attack speed"
    assert tier.effects[1].description == "Adds stun chance"


def test_synergy():
    """Test Synergy model."""
    synergy = Synergy(
        name="Attack Speed",
        description="Increases attack speed",
        tiers=[
            SynergyTier(
                required=3,
                effects=[
                    SynergyEffect(
                        description="Increases attack speed",
                        value=10.0,
                        unit="percentage"
                    )
                ]
            ),
            SynergyTier(
                required=6,
                effects=[
                    SynergyEffect(
                        description="Increases attack speed",
                        value=25.0,
                        unit="percentage"
                    )
                ]
            )
        ]
    )
    
    assert synergy.name == "Attack Speed"
    assert synergy.description == "Increases attack speed"
    assert len(synergy.tiers) == 2
    assert synergy.tiers[0].required == 3
    assert synergy.tiers[1].required == 6


def test_game_synergies():
    """Test GameSynergies model."""
    synergies = GameSynergies(
        critical_hit=SynergyGroup(
            gems=["ruby", "sapphire"],
            essences=["fire", "water"],
            skills=["fireball", "ice_bolt"]
        ),
        movement_speed=SynergyGroup(
            gems=["emerald"],
            essences=["wind"],
            skills=["dash"]
        ),
        damage_boost=None
    )
    
    assert isinstance(synergies.critical_hit, SynergyGroup)
    assert isinstance(synergies.movement_speed, SynergyGroup)
    assert synergies.damage_boost is None
    
    assert len(synergies.critical_hit.gems) == 2
    assert len(synergies.movement_speed.gems) == 1
