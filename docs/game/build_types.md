# Build Types Configuration

This document describes the configuration structure for build types in the game. The configuration is stored in `data/indexed/build_types.json`.

## Overview

The build types configuration defines how different skills are scored based on their
type, description, and mechanics. This allows for flexible adjustment of build
generation without code changes.

### Dynamic Build Types

The configuration supports dynamic build types, allowing users to define custom
build types beyond the standard raid, farm, and pvp types. For example:

```json
{
  "fast_farm": {
    "dps": {
      "terms": ["speed", "quick", "rapid", "swift"],
      "score_weights": {
        "base_type_match": 0.4,
        "term_match": 0.3,
        "cooldown": {
          "threshold": 5,
          "score": 0.3
        }
      }
    }
  }
}
```

When adding new build types:

1. Choose a descriptive name (e.g., `fast_farm`, `boss_raid`, `group_pvp`)
2. Define appropriate terms and weights
3. Consider cooldown thresholds for the specific use case
4. Document the new build type's purpose and scoring logic

## File Structure

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "ISO-8601 timestamp"
  },
  "build_types": {
    "[build_type]": {
      "[focus]": {
        "terms": ["..."],
        "score_weights": {
          "base_type_match": float,
          "second_type_match": float,
          "term_match": float,
          "cooldown": {
            "threshold": int,
            "threshold_medium": int,
            "score": float,
            "score_medium": float
          }
        }
      }
    }
  }
}
```

## Configuration Fields

### Build Types

Each build type (raid, farm, pvp) can have multiple focuses:

- `raid`: Focused on boss fights and sustained damage
- `farm`: Optimized for efficient resource gathering
- `pvp`: Balanced for player versus player combat

### Focus Types

Each build type can have different focuses:

- `dps`: Damage dealing
- `survival`: Defense and sustain
- `buff`: Support and enhancement

### Scoring Configuration

#### Terms

Lists of keywords that, when found in skill descriptions, contribute to the skill's
score. Example:

```json
"terms": [
  "damage over time",
  "area damage",
  "nearby enemies"
]
```

#### Score Weights

Defines how different aspects contribute to the final skill score:

- `base_type_match`: Score for matching primary skill type (0.0-1.0)
- `second_type_match`: Score for matching secondary skill type (0.0-1.0)
- `term_match`: Score for matching terms in description (0.0-1.0)

#### Cooldown Configuration

Optional cooldown scoring parameters:

- `threshold`: Primary cooldown threshold in seconds
- `threshold_medium`: Secondary cooldown threshold in seconds
- `score`: Score for meeting primary threshold (0.0-1.0)
- `score_medium`: Score for meeting secondary threshold (0.0-1.0)

## Example Configuration

Here's an example for a raid DPS configuration:

```json
{
  "raid": {
    "dps": {
      "terms": [
        "damage over time",
        "area damage",
        "nearby enemies"
      ],
      "score_weights": {
        "base_type_match": 0.5,
        "second_type_match": 0.3,
        "term_match": 0.2,
        "cooldown": {
          "threshold": 15,
          "score": 0.2
        }
      }
    }
  }
}
```

## Usage

The build service uses this configuration to score skills when generating builds:

1. Matches skill type against focus
2. Searches for terms in skill description
3. Evaluates cooldown thresholds
4. Combines scores using weights

## Maintenance

### Adding New Terms

When adding new terms:

1. Ensure terms match actual in-game text
2. Add terms that appear in skill descriptions
3. Keep terms specific and meaningful
4. Document term additions in changelog

### Adjusting Weights

When modifying weights:

1. Test changes with multiple builds
2. Keep total possible score ≤ 1.0
3. Document weight changes in changelog
4. Consider impact on existing builds

## Version History

### 1.0.0 (2025-01-10)

- Initial release
- Basic configuration for raid, farm, and pvp builds
- Support for DPS, survival, and buff focuses
