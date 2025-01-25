# Classes Data Structure

This directory contains indexed data for all classes in the game.

## Directory Structure

```text
classes/
├── README.md                    # This file
├── index.json                  # Global class metadata and references
├── barbarian/                  # Each class has its own directory
│   ├── metadata/              # Class-specific metadata
│   │   ├── skills.json       # Skill descriptions and stats
│   │   ├── mechanics.json    # Class mechanics and special features
│   │   └── stats.json        # Base stats and scaling
│   ├── essences/             # Split essences by slot
│   │   ├── helm.json        # Helm essences
│   │   ├── shoulder.json    # Shoulder essences
│   │   ├── chest.json       # Chest essences
│   │   ├── legs.json        # Legs essences
│   │   ├── main_hand.json   # Main hand essences
│   │   └── off_hand.json    # Off-hand essences
│   └── indexes/              # Various indexes for quick lookups
│       ├── by_slot.json     # Essences indexed by equipment slot
│       ├── by_skill.json    # Essences indexed by modified skill
│       └── by_effect.json   # Essences indexed by effect type
└── [other classes]/          # Same structure for other classes
```

## File Formats

### index.json

Global metadata about all classes:

```json
{
  "version": "1.0.0",
  "last_updated": "YYYY-MM-DD",
  "classes": {
    "barbarian": {
      "name": "Barbarian",
      "description": "...",
      "total_essences": 153
    }
  }
}
```

### metadata/skills.json

```json
{
  "skills": {
    "skill_name": {
      "description": "...",
      "essence_count": 10
    }
  }
}
```

### essences/[slot].json

```json
{
  "metadata": {
    "slot": "helm",
    "essence_count": 25
  },
  "essences": {
    "essence_id": {
      "essence_name": "Name",
      "modifies_skill": "Skill",
      "effect": "Description",
      "effect_type": "damage",
      "tags": ["tag1", "tag2"]
    }
  }
}
```

### indexes/by_slot.json

```json
{
  "Helm": ["essence_id1", "essence_id2"],
  "Shoulder": ["essence_id3", "essence_id4"]
}
```

## Usage

1. Use the class-specific metadata files to get information about skills and mechanics
2. Use the essence files to get detailed information about specific essences
3. Use the index files for quick lookups and filtering

## Updating Data

1. Update the relevant essence file in the essences/ directory
2. Update any affected indexes
3. Update the metadata counts if necessary
