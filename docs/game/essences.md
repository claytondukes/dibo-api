# Essence System

## Overview

The Essence system in Diablo Immortal allows players to modify their skills through legendary items. Each class has unique essences that can be extracted from legendary items and transferred to other items of the same slot.

## Core Concepts

### Essence Transfer

- Essences can be extracted from legendary items
- Extracted essences can be applied to other items in the same slot
- Each gear piece can hold one essence effect
- Effects are class-specific and skill-specific

### Gear Slots

Essences can be found on and transferred between:

- Helm
- Chest
- Shoulders
- Legs
- Main Hand weapons
- Off-Hand items

## Class Implementation

### Barbarian Example

Total Essences: 72

Skills with Essence Modifications:

1. Demoralize (11 variations)
   - Crowd control and damage modifications
   - Example: "Demoralize now pulls in all nearby enemies"

2. Sprint (7 variations)
   - Movement and offensive capabilities
   - Example: "Sprint increases Critical Hit Chance by 19% while moving"

3. Ground Stomp (9 variations)
   - Area control and damage
   - Example: "Ground Stomp rips open the ground, dealing damage; max 2 charges"

4. Whirlwind (10 variations)
   - Sustained damage and effects
   - Example: "Whirlwind shreds armor, +2% damage taken per hit (stack up to 5x)"

5. Iron Skin (5 variations)
   - Defensive modifications
   - Example: "Iron Skin grants 20% increased damage reduction"

6. Leap (7 variations)
   - Mobility and offensive capabilities
   - Example modifications for landing effects and damage

## Data Structure

### Static Data (in indexed/)

Located in `data/indexed/classes/<class_name>/essences.json`:

```json
{
  "metadata": {
    "version": "1.0.0",
    "class": "ClassName",
    "total_essences": N
  },
  "essences": {
    "essence_id": {
      "essence_name": "Name",
      "gear_slot": "Slot",
      "modifies_skill": "SkillName",
      "effect": "Description"
    }
  },
  "indexes": {
    "by_slot": {
      "Slot": ["essence_ids"]
    }
  }
}
```

### Dynamic Data (in GitHub Gists)

Player-specific essence data includes:

- Extracted essences collection
- Currently applied essences
- Essence transfer history

## API Implementation Notes

When implementing essence-related endpoints:

1. Query available essences from indexed data
2. Track player's extracted essences
3. Validate essence transfer rules:
   - Same slot requirement
   - Class restrictions
   - One essence per item
4. Handle extraction and application operations
5. Update player's essence collection
6. Consider essence effects in build calculations
