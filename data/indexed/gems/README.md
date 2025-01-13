# Gem Data Structure Documentation

Last Updated: 2025-01-12T15:00:53-05:00

## Overview

This directory contains the structured data for all gems, their effects, conditions, and synergies. The data is organized into a modular structure to minimize redundancy and maintain a single source of truth for each type of information.

## Directory Structure

```
data/indexed/gems/
├── core/                    # Individual gem files
│   ├── 1star/              # 1-star gems
│   ├── 2star/              # 2-star gems
│   └── 5star/              # 5-star gems
├── deprecated/             # Deprecated files (for reference)
├── metadata/               # Metadata and relationship files
│   ├── conditions.json     # All gem conditions
│   ├── effect_details.json # Detailed effect information
│   ├── gem_skillmap.json   # Gem to skill mappings
│   ├── stat_boosts/        # Stat boost details
│   └── synergies/          # Synergy-related files
└── index.json             # Gem name to path mapping
```

## File Formats

### Individual Gem Files (`core/{1,2,5}star/*.json`)

Each gem has its own JSON file containing core properties and effects:

```json
{
  "name": "Gem Name",
  "stars": "2",
  "ranks": {
    "1": {
      "effects": [
        {
          "type": "effect_type",
          "description": "Effect description",
          "conditions": ["condition1", "condition2"]
        }
      ]
    }
  }
}
```

### Metadata Files

#### `conditions.json`

Maps gem names to their conditions with detailed patterns and descriptions:

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "timestamp"
  },
  "conditions": {
    "Gem Name": [
      {
        "type": "trigger|state|effect_category",
        "trigger": "trigger_name",
        "description": "Human readable description",
        "pattern": "regex pattern"
      }
    ]
  }
}
```

#### `effect_details.json`

Contains detailed information about specific effects:

```json
{
  "effect_details": {
    "control_effects": {
      "Gem Name": {
        "effect_type": {
          "chance": number,
          "duration": number,
          "cooldown": number
        }
      }
    },
    "health_thresholds": {
      "Gem Name": {
        "above|below": number
      }
    },
    "cooldowns": {
      "Gem Name": number
    },
    "dot_effects": {
      "Gem Name": {
        "duration": number,
        "type": "effect_type"
      }
    }
  }
}
```

#### `gem_skillmap.json`

Maps skills to gems that affect them:

```json
{
  "gems_by_skill": {
    "skill_name": ["Gem1", "Gem2"]
  }
}
```

#### Synergies Directory (`metadata/synergies/`)

##### `categories.json`

Groups gems by their primary function:

```json
{
  "categories": {
    "category_name": {
      "description": "Category description",
      "gems": ["Gem1", "Gem2"]
    }
  }
}
```

##### `gem_pairs.json`

Documents synergies between specific gem pairs:

```json
{
  "pairs": {
    "Gem1": {
      "Gem2": {
        "score": number,
        "description": "Synergy description",
        "build_types": ["type1", "type2"],
        "focus": ["focus1", "focus2"]
      }
    }
  }
}
```

##### `skill_gems.json`

Details how gems interact with different skill types:

```json
{
  "Gem Name": {
    "skill_types": {
      "skill_type": {
        "score": number,
        "description": "Interaction description",
        "build_types": ["type1", "type2"]
      }
    }
  }
}
```

### Root Files

#### `index.json`

Maps gem names to their file paths:

```json
{
  "Gem Name": "core/Nstar/gem_file.json"
}
```

## Usage Guidelines

1. **Single Source of Truth**:
   - Conditions are stored in `conditions.json`
   - Categories are stored in `synergies/categories.json`
   - Effect details are stored in `effect_details.json`

2. **File Updates**:
   - Always update the `last_updated` timestamp in metadata sections
   - Keep deprecated files for reference in the `deprecated/` directory
   - Maintain consistent formatting and structure

3. **Adding New Gems**:
   - Create gem file in appropriate star directory
   - Add to `index.json`
   - Add conditions to `conditions.json`
   - Update relevant metadata files

4. **Validation**:
   - Ensure all referenced conditions exist in `conditions.json`
   - Verify all gem paths in `index.json` are valid
   - Check that all required metadata is present

## Best Practices

1. **Code Organization**:
   - Keep gem files minimal, referencing metadata where possible
   - Use consistent naming conventions
   - Maintain proper JSON formatting

2. **Documentation**:
   - Update this README when making structural changes
   - Document complex patterns or relationships
   - Keep examples up to date

3. **Data Integrity**:
   - Validate all changes before committing
   - Keep metadata files in sync
   - Maintain backwards compatibility when possible

## Maintenance

- Regularly review deprecated files for cleanup
- Update patterns and descriptions as needed
- Monitor file sizes and consider optimization if needed
- Keep documentation current with any changes
