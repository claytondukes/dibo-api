---
name: Character Class Data Implementation
about: Template for implementing new character class JSON data files
title: 'feat: Implement [Class Name] JSON Data Files'
labels: help-wanted, good-first-issue, enhancement, data, game-design
assignees: ''
---

# Help Wanted: Create Character Class JSON Data Files

## Overview

We need help creating JSON data files for additional character classes in our
Diablo-style game API. We have a complete set of files for the Barbarian class
that can serve as a template.

## Required Files

For each character class, we need three JSON files:

1. `base_skills.json`: Core skill definitions
   - Base type and secondary type
   - Base cooldowns
   - Skill descriptions

2. `constraints.json`: Class-specific constraints
   - Available skills list
   - Available weapon types

3. `essences.json`: Class-specific gear modifications
   - Metadata about the class
   - Detailed essence effects for each skill
   - Gear slot information
   - Indexes for quick lookups

## Example Structure

The Barbarian class files in `data/indexed/classes/barbarian/` serve as our
reference implementation:

```json
// base_skills.json example
{
  "registry": {
    "Cleave": {
      "base_type": "damage",
      "second_base_type": null,
      "base_cooldown": "6",
      "description": "Unleash a powerful attack..."
    }
  }
}

// constraints.json example
{
  "skill_slots": {
    "available_skills": [
      "Hammer of the Ancients",
      "Cleave",
      "Whirlwind"
    ]
  },
  "weapon_slots": {
    "available_weapons": [
      "Frenzy"
    ]
  }
}

// essences.json example
{
  "metadata": {
    "version": "1.0.0",
    "class": "Barbarian",
    "total_essences": 72
  },
  "essences": {
    "visage_of_the_living_ancients": {
      "essence_name": "Visage of the Living Ancients",
      "gear_slot": "Helm",
      "modifies_skill": "Demoralize",
      "effect": "..."
    }
  }
}
```

## How to Contribute

1. Pick an unimplemented class
2. Create a new directory in `data/indexed/classes/[class_name]/`
3. Create all three JSON files following our Barbarian template
4. Ensure JSON is valid and properly formatted
5. Submit a PR with your implementation

## Requirements

- Follow existing naming conventions
- Maintain consistent JSON structure
- Provide realistic and balanced skill descriptions
- Include appropriate cooldowns and effects
- Ensure gear slot compatibility
- Add comprehensive metadata

## Definition of Done

- [ ] Created directory for new class
- [ ] Implemented `base_skills.json`
- [ ] Implemented `constraints.json`
- [ ] Implemented `essences.json`
- [ ] Validated JSON formatting
- [ ] Verified skill balance and descriptions
- [ ] Updated metadata appropriately
- [ ] Tested gear slot compatibility
