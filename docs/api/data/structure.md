# Data Structure Documentation

## Overview

This document describes the data structure used by the DIBO API. The data is organized in a hierarchical structure under the `data/indexed` directory, with clear separation between global data, class-specific data, and shared mechanics.

## Directory Structure

```
data/indexed/
├── classes/                    # Class-specific data
│   └── barbarian/             # Barbarian class data
│       ├── base_skills.json   # Base skill definitions
│       ├── constraints.json   # Class-specific constraints
│       └── essences.json      # Essence definitions and indexes
├── gems/                      # Gem-related data
│   ├── progression.json      # Gem upgrade progression
│   ├── stat_boosts.json      # Detailed gem stat modifications
│   ├── synergies.json       # Gem synergy definitions
│   └── gems.json           # Core gem definitions
├── equipment/                # Equipment-related data
│   └── sets.json            # Set bonus definitions
├── metadata.json            # Data versioning and updates
├── synergies.json           # Global synergy definitions
├── constraints.json         # Global build constraints
└── stats.json              # Base stat definitions
```

## Data Formats

### metadata.json
Version and update tracking:
```json
{
  "last_updated": "ISO-8601 timestamp",
  "version": "string",
  "data_structure_version": "string"
}
```

### Class Data

#### base_skills.json
```json
{
  "metadata": { "version": "string" },
  "skills": {
    "skill_name": {
      "base_type": "primary",
      "description": "string",
      "tags": ["mobility", "damage"],
      "cooldown": "number"
    }
  }
}
```

#### essences.json
```json
{
  "metadata": { "version": "string" },
  "essences": {
    "essence_id": {
      "name": "string",
      "slot": "string",
      "skill": "string",
      "effect": "string",
      "tags": ["string"],
      "type": "legendary"
    }
  },
  "indexes": {
    "by_slot": { "slot_name": ["essence_id"] },
    "by_skill": { "skill_name": ["essence_id"] },
    "by_type": { "type_name": ["essence_id"] }
  }
}
```

### Gem Data

#### stat_boosts.json
```json
{
  "stat_name": {
    "gems": [
      {
        "name": "string",
        "stars": "string",
        "base_values": [
          {
            "conditions": ["string"],
            "value": "number",
            "unit": "string",
            "scaling": "boolean"
          }
        ],
        "rank_10_values": [],
        "conditions": ["string"],
        "rank_10_conditions": ["string"]
      }
    ],
    "essences": []
  }
}
```

#### progression.json
```json
{
  "metadata": { "version": "string" },
  "gems": {
    "gem_name": {
      "ranks": ["number"],
      "resonance": ["number"],
      "requirements": {
        "rank": {
          "gem_power": "number",
          "duplicate_gems": "number"
        }
      }
    }
  }
}
```

### Equipment Data

#### sets.json
```json
{
  "metadata": { "version": "string" },
  "sets": {
    "set_name": {
      "pieces": ["string"],
      "bonuses": {
        "2": "string",
        "4": "string",
        "6": "string"
      },
      "tags": ["string"]
    }
  }
}
```

### Global Data

#### synergies.json
```json
{
  "synergy_type": {
    "gems": ["string"],
    "essences": ["string"],
    "skills": ["string"],
    "conditions": {
      "item_name": [
        {
          "type": "string",
          "trigger": "string",
          "text": "string"
        }
      ]
    }
  }
}
```

#### constraints.json
```json
{
  "gem_slots": {
    "total_required": "number",
    "primary": {
      "required": "number",
      "unique": "boolean",
      "star_ratings": ["number"]
    }
  }
}
```

## Data Management

### Version Control
- All data files include metadata with version information
- `metadata.json` tracks global data structure version
- Changes to data structure require version updates

### Organization
- Global data in root directory
- Class-specific data in class directories
- Shared mechanics in dedicated directories

### Type System
- All numeric values specify units where applicable
- Boolean flags for scaling and unique requirements
- Consistent use of string enums for types

### File Naming
- All JSON files use snake_case
- Directories use lowercase
- Clear separation of concerns in file structure

## Related Documentation
- [API Documentation](../v1.md) - API endpoints and responses
- [Data Tests](../tests/data/data.md) - Data validation and testing
