# Indexed Data Structure

This directory contains indexed game data used by the API. The data is organized into the following structure:

## Directory Structure

```text
data/indexed/
├── classes/                    # Class-specific data
│   └── barbarian/             # Data for Barbarian class
│       ├── base_skills.json   # Base skills for Barbarian, these are default players skills and should not be used unless it is intentinal. Most builds will want to use a different essence.
│       ├── constraints.json   # Class-specific constraints
│       └── essences.json      # Class-specific essences
├── equipment/                 # Equipment data
│   └── sets.json             # Set definitions and bonuses
├── gems/                     # Gem-related data
│   ├── gem_skillmap.json    # Mapping between gems and skills
│   ├── gems.json           # Core gem definitions
│   ├── stat_boosts.json   # Gem stat boost effects
│   └── synergies.json    # Gem synergy effects
├── constraints.json      # Global game constraints
├── metadata.json       # Data version and update info
├── stats.json        # Core game stats
└── synergies.json   # Global synergy definitions
```

## Data Files

### Core Files

- `metadata.json`: Version information and last update timestamp
- `stats.json`: Core game stats and calculations
- `synergies.json`: Global synergy definitions
- `constraints.json`: Global game constraints

### Class-Specific Files

Each class has its own directory under `classes/` containing:

- `base_skills.json`: Class-specific skills and abilities
- `constraints.json`: Class-specific constraints and requirements
- `essences.json`: Class-specific essence modifications

### Equipment System

The equipment system has two distinct categories, both with static slot definitions:

#### 1. Main Gear Slots (Right Side)

These slots are constants and never change:

- Head (Helm)
- Chest (Torso armor)
- Shoulders
- Legs
- Main Hand (Set 1)
- Off Hand (Set 1)
- Main Hand (Set 2)
- Off Hand (Set 2)

#### 2. Set Gear Slots (Left Side)

These slots are also constants, but can be filled with different set pieces:

- Neck
- Waist
- Hands
- Feet
- Ring 1
- Ring 2
- Bracer 1
- Bracer 2

The actual set pieces that can be equipped in these slots are defined in:

- `equipment/sets.json`: Defines available sets and their bonuses
  - Each set (like "Grace of the Flagellant") can have pieces equipped in any set slot
  - Sets provide bonuses at 2/4/6 piece thresholds
  - Set bonuses are cumulative (6 pieces = 2pc + 4pc + 6pc bonuses)

### Gem Files

- `gems/gems.json`: Core gem definitions and properties
- `gems/stat_boosts.json`: Gem stat boost effects
- `gems/synergies.json`: Gem synergy effects
- `gems/gem_skillmap.json`: Mapping between gems and skills

## Adding New Classes

When adding a new class:

1. Create a new directory under `classes/` with the class name
2. Add the required class-specific files:
   - `base_skills.json`
   - `constraints.json`
   - `essences.json`
3. Update relevant code to handle the new class data

## Data Validation

The API performs validation of this structure at startup. See:

- `api/models/game_data/data_manager.py` for data loading
- `api/builds/service.py` for build-specific data handling
