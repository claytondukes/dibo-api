# Gem Synergy Templates

This directory contains predefined templates for various gem builds optimized for different content types and playstyles.

## Directory Structure

```text
templates/
├── pve/                 # PvE-focused templates
│   ├── raid.json       # Raid optimization builds
│   ├── dps.json        # Pure damage builds
│   └── farm.json       # Farming efficiency builds
│
└── pvp/                 # PvP-focused templates
    ├── survival.json   # Pure survival builds
    ├── counter.json    # Counter-damage builds
    ├── control.json    # Crowd control builds
    ├── dps.json        # Burst damage builds
    └── dot.json        # DOT-focused builds
```

## Template Types

### PvE Templates

- **Raid**: Optimized for raid content, focusing on sustained damage and mechanics
- **DPS**: Pure damage builds for maximum output in PvE content
- **Farm**: Efficient farming builds optimized for speed and resource gathering

### PvP Templates

- **Survival**: Maximum survivability and damage mitigation
- **Counter**: Reflects and converts incoming damage
- **Control**: Crowd control and lockdown mechanics
- **DPS**: Burst damage for securing kills
- **DOT**: Damage over time pressure and spread

## Template Format

Each template file follows a standard JSON structure:

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "YYYY-MM-DDThh:mm:ss-00:00"
  },
  "templates": {
    "template_id": {
      "name": "Template Name",
      "description": "Template description",
      "primary_type": "pvp|pve",
      "role_type": "role_type",
      "gem_sets": {
        "primary_set": {
          "gems": [...],
          "synergy_groups": [...]
        }
      },
      "stat_priorities": {
        "primary": [...],
        "secondary": [...]
      }
    }
  }
}
```

## Usage Guidelines

1. Each template focuses on a specific purpose without mixing intents
2. Templates can be combined through the build generator
3. PvP templates emphasize normalized scaling mechanics
4. PvE templates balance Combat Rating with synergies

## Maintenance

- Keep template files focused on a single purpose
- Update the `last_updated` timestamp when making changes
- Document all gem interactions and synergies
- Test templates in their intended content type
- Consider both solo and group play implications

## Contributing

When adding new templates:

1. Follow the established JSON structure
2. Place in the appropriate pve/pvp directory
3. Focus on a single, clear purpose
4. Document all gem interactions
5. Include stat priorities
6. Consider content-specific mechanics
7. Test thoroughly before committing
