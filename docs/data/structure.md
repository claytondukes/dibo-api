# Data Directory Structure

## Overview

The `data/indexed` directory contains all game data used by the API. This data is organized into several subdirectories based on their purpose and scope.

## Directory Structure

```
data/indexed/
├── classes/                    # Class-specific data
│   └── barbarian/             # Barbarian class data
│       ├── base_skills.json   # Base skill definitions
│       ├── constraints.json   # Available skills and weapons
│       └── essences.json      # Essence definitions and indexes
├── gems/                      # Gem-related data
│   ├── progression.json      # Gem upgrade progression
│   ├── stat_boosts.json      # Gem stat boost values
│   ├── synergies.json       # Gem synergy definitions
│   └── gems.json           # Gem effect definitions
├── equipment/                # Equipment-related data
│   └── sets.json            # Set bonus definitions
├── synergies.json           # Global synergy definitions
├── constraints.json         # Global build constraints
└── stats.json              # Base stat definitions
```

## Directory Descriptions

### classes/
Contains class-specific data organized by character class. Each class has its own subdirectory containing data that only applies to that class.

#### barbarian/
Data specific to the Barbarian class.
- `base_skills.json`: Base skill definitions and properties.
- `constraints.json`: Available skills and weapons for the Barbarian class.
- `essences.json`: Complete essence data with optimized structure:
  ```json
  {
    "metadata": {
      "version": "string",
      "last_updated": "string"
    },
    "essences": {
      "essence_id": {
        "name": "string",
        "slot": "string",
        "skill": "string",
        "effect": "string",
        "tags": ["string"]
      }
    },
    "indexes": {
      "by_slot": {
        "slot_name": ["essence_id"]
      },
      "by_skill": {
        "skill_name": ["essence_id"]
      }
    }
  }
  ```

### gems/
Contains all gem-related data files.
- `progression.json`: Defines gem upgrade paths and requirements.
- `stat_boosts.json`: Contains gem stat boost values at different ranks.
- `synergies.json`: Defines synergies between different gems.
- `gems.json`: Defines gem effects and properties.

### equipment/
Contains equipment-related data files.
- `sets.json`: Set bonus definitions and requirements.

### Root Files
- `synergies.json`: Global synergy definitions.
- `constraints.json`: Global build constraints (non-class-specific).
- `stats.json`: Base stat definitions.

## Notes

1. Class Organization:
   - Each class has its own directory under `classes/`
   - Class-specific files are contained within their respective directories
   - Global constraints are separate from class-specific constraints

2. Equipment System:
   - Primary gear: Can have essence modifications and legendary gem slots
   - Set gear ("greens"): Part of equipment sets, cannot have essence modifications or legendary gem slots

3. File Organization:
   - Global data is in root directory
   - Class-specific data is in class directories
   - Shared mechanics (gems) have their own directories

4. Inventory Management:
   - Player inventory is stored in GitHub Gists
   - Inventory includes owned gems, their ranks, and quality levels

5. File Naming Conventions:
   - All JSON files use snake_case
   - Directory names use lowercase
   - Class names match their in-game names (e.g., "barbarian")

6. Essence Structure:
   - Single source of truth in `essences.json`
   - Optimized indexes for fast lookups by slot and skill
   - Includes metadata for version tracking
   - Tags for categorizing effects (e.g., "damage", "control", "utility")

7. Data Validation:
   - All JSON files must be valid according to their schemas
   - Required fields are enforced at runtime
   - Cross-references between files are validated during API startup
