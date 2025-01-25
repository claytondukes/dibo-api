# Essence System

## Overview

The Essence system in Diablo Immortal allows players to modify their skills through legendary items. Each class has unique essences that can be extracted from legendary items and transferred to other items of the same slot.

## Core Concepts

### Essence Transfer

- Essences can be extracted from legendary items
- Extracted essences can be applied to other items in the same slot
- Each gear piece can hold one essence effect
- Effects are class-specific and skill-specific
- Each unique essence can only be used once across all slots
- Duplicate essences are not allowed, even across different weapon sets

### Gear Slots

Essences can be found on and transferred between:

- Helm (25 essences)
- Chest (20 essences)
- Shoulders (25 essences)
- Legs (24 essences)
- Main Hand weapons (26 essences)
- Off-Hand items (24 essences)

## Data Structure

The essence data is organized in a hierarchical structure:

```text
/data/indexed/classes/{class_name}/
  ├── essences/
  │   ├── helm.json
  │   ├── chest.json
  │   ├── shoulder.json
  │   ├── legs.json
  │   ├── main_hand.json
  │   └── off_hand.json
  ├── metadata/
  │   ├── skills.json      # Skill descriptions and essence counts
  │   └── mechanics.json   # Effect types and tags
  └── indexes/
      ├── by_slot.json     # Quick lookup by equipment slot
      ├── by_skill.json    # Quick lookup by modified skill
      └── by_effect.json   # Quick lookup by effect type
```

### File Format

Each essence file follows this structure:

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "YYYY-MM-DDThh:mm:ss-05:00",
    "slot": "slot_name",
    "essence_count": N
  },
  "essences": {
    "essence_id": {
      "essence_name": "Display Name",
      "modifies_skill": "Skill Name",
      "effect": "Effect Description",
      "effect_type": "damage|utility|defense",
      "tags": ["tag1", "tag2"]
    }
  }
}
```

## Class Implementation

### Barbarian

Total Essences: 144

Distribution by Slot:

- Helm: 25 essences
- Chest: 20 essences
- Shoulders: 25 essences
- Legs: 24 essences
- Main Hand: 26 essences
- Off-Hand: 24 essences

Effect Types:

- Damage: Direct damage increases, new damage effects
- Utility: Cooldown reduction, resource generation, crowd control
- Defense: Damage reduction, healing, shields

Common Tags:

- damage_boost
- cooldown
- resource
- aoe
- dot
- proc
- movement_speed
- conditional
