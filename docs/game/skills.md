# Diablo Immortal Skills Guide

## Skill System Overview

The skill system in Diablo Immortal is highly customizable through various game elements. Each character can equip 4 skills plus a weapon skill, and these skills can be modified through multiple systems.

### Base Skills

Skills are categorized by their base types:

- **Damage**: Primary damage-dealing skills (e.g., Hammer of the Ancients, Cleave)
- **Control**: Crowd control abilities (e.g., Ground Stomp, Grab)
- **Buff**: Self-enhancement abilities (e.g., Sprint, Wrath of the Berserker)
- **Dash**: Movement abilities (e.g., Furious Charge, Sunder)
- **Channel**: Sustained abilities (e.g., Whirlwind)

Some skills have secondary types that provide additional functionality:

- **Multiple-stage**: Skills with distinct phases (e.g., Grab)
- **Charge**: Skills that can be charged for enhanced effects (e.g., Ground Stomp)
- **Channel**: Skills that can be maintained (e.g., Whirlwind)

### Skill Slots

Characters have access to:

- 1 primary weapon skill slot (must be a weapon skill like Frenzy or Lacerate)
- 4 secondary skill slots (non-weapon skills)

This means a total of 5 skills can be equipped at once.

### Cooldown Categories

Skills are divided into cooldown categories:

- **No Cooldown**: Basic abilities that can be used constantly
- **Short** (0-10s): Frequently available abilities
- **Medium** (11-20s): Tactical abilities
- **Long** (>20s): Major cooldown abilities

## Skill Modification Systems

Skills can be modified through various game systems:

### 1. Essence System

- Direct skill modifications through legendary essences
- Each skill can be modified by specific essences
- Essences are tied to specific gear slots

### 2. Set Bonuses

Modify skill types:

- Primary attack modifications
- Channeled skill enhancements
- Movement skill boosts
- Summon-based improvements
- AoE damage increases

### 3. Gem Effects

Can enhance:

- Primary attack speed/damage
- Critical hit chance/damage
- Movement speed
- Attack speed
- Beneficial effect duration

### 4. Enchantments

Provide stat boosts to:

- Primary attack damage
- Critical hit stats
- Beneficial effect duration
- Overall damage output

## Skill Modifications

Skills can be modified through various systems:

### 1. Essence Modifications

- Legendary essences that modify skill behavior
- Each skill can have multiple essence options
- Only one essence per skill can be active
- Essences are categorized by:
  - Gear slot (e.g., Helm, Chest)
  - Modified skill
  - Effect type (e.g., damage, control)
- Effects can include:
  - Behavior changes (e.g., skill becomes a projectile)
  - Damage modifiers
  - Added effects (e.g., stun, knockback)
  - Resource modifications

### 2. Gem Effects

- Legendary gems that enhance skills
- Can affect specific skills or all skills
- Multiple gems can affect the same skill

### 3. Set Bonuses

- Equipment set combinations
- Provide skill-specific or general bonuses
- Stack with essence modifications

## Skill Synergies

Skills can synergize through:

### 1. Direct Combinations

- Skills that work well together (e.g., control + damage)
- Movement skills into damage skills

### 2. Essence Synergies

- Essences that complement each other
- Effects that chain together

### 3. Build Focus

- PvE vs PvP optimization
- Single target vs AoE damage
- Burst vs sustained damage

## Skill Data Structure

The skill system data is organized in several JSON files:

### skills/registry.json

- Base skill information
- Skill types and cooldowns
- Basic descriptions

### skills/essence_modifications.json

- Direct skill-to-essence mappings
- Modification effects
- Required gear slots

### skills/modifiers.json

Organized in three ways:

1. **By Skill**: Direct modifications to specific skills
2. **By Type**: Modifications affecting skill categories
3. **By Source**: Groups modifications by their source

## Build Considerations

When building around skills:

1. **Base Selection**
   - Choose skills that complement each other
   - Consider cooldown distribution
   - Balance damage, control, and utility

2. **Modification Planning**
   - Match essences to core skills
   - Select sets that enhance skill types
   - Choose gems that boost skill performance
   - Add enchantments for stat optimization

3. **Synergy Focus**
   - Combine skills with complementary effects
   - Stack modifiers from different sources
   - Consider proc conditions and uptimes
