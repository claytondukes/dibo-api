# Stat Boost System Documentation

## Overview

The Stat Boost system tracks how gems modify character stats in Diablo Immortal. Each gem can provide one or more stat boosts, with values that may scale based on rank and conditions.

**Note**: While both gems and essences can modify primary gear, they work through different systems:

- Gems provide stat boosts (tracked here)
- Essences modify skill behavior (see @[docs/game/essences.md])

## Core Concepts

### Stat Categories

Stats are organized into the following categories:

1. **Critical Hit Chance**: Increases the chance to deal critical hits
2. **Critical Hit Damage**: Increases the damage dealt by critical hits
3. **Damage Increase**: Increases all damage dealt
4. **Attack Speed**: Increases attack speed
5. **Movement Speed**: Increases movement speed
6. **Life**: Increases maximum life

### Gem Stat Boosts

Each gem entry contains:

1. Base values (rank 1)
2. Rank 10 values
3. Conditions that affect when the stats apply

## File Structure

The stat boost data is stored in `data/indexed/gems/stat_boosts.json`. Each stat category contains:

1. **gems**: Array of gems that provide this stat
2. **description**: Purpose of this stat category

Example structure:

```json
{
  "critical_hit_chance": {
    "gems": [
      {
        "name": "Chained Death",      // Name of the gem
        "stars": "2",                 // Rarity rating (1-5 stars)
        "base_values": [              // Stats at rank 1
          {
            "conditions": [           // Conditions for the stat to apply
              {
                "type": "cooldown",
                "cooldown": 20.0,
                "text": "cannot occur more often than once every 20 seconds"
              }
            ],
            "value": 8.0,            // Numerical value of the stat
            "unit": "percentage",     // Unit type (percentage, flat)
            "scaling": false          // Whether value scales with conditions
          }
        ],
        "rank_10_values": [          // Stats at max rank
          {
            "conditions": [],         // Empty means always active
            "value": 16.0,
            "unit": "percentage",
            "scaling": false
          }
        ]
      }
    ],
    "description": "Increases the chance to deal critical hits"
  }
}
```

## Condition Types and Examples

### 1. Cooldown Conditions

```json
{
  "type": "cooldown",
  "cooldown": 20.0,
  "text": "cannot occur more often than once every 20 seconds"
}
```

Specifies how often an effect can trigger. Common in:

- Proc effects (e.g., "Blessing of the Worthy" unleashing retribution)
- State changes (e.g., "Mother's Lament" entering Maternal Disdain)
- Damage effects (e.g., "Lightning Core" chain lightning)

### 2. State Conditions

```json
{
  "type": "state",
  "state": "health_threshold",
  "text": "below 50% Life",
  "threshold": 50.0
}
```

Represents persistent conditions about the character's state:

- Health thresholds (e.g., "below 50% Life", "at full Life")
- Buffs/Debuffs (e.g., "while Chilled", "during Maternal Disdain")
- Combat state (e.g., "while in combat", "after defeating an enemy")

### 3. Trigger Conditions

```json
{
  "type": "trigger",
  "trigger": "on_attack",
  "text": "your attacks"
}
```

Defines events that activate the stat boost:

- Combat actions (e.g., "when you attack", "on hit")
- Movement (e.g., "while moving", "when stationary")
- Skill usage (e.g., "when using Primary Attack", "after using a skill")

### 4. Distance Conditions

```json
{
  "type": "distance",
  "distance": 8.0,
  "text": "at 8 yards"
}
```

Specifies distance-based requirements:

- Range checks (e.g., "for every 2 yards between you and the enemy")
- Area effects (e.g., "to nearby enemies within 6 yards")
- Position bonuses (e.g., "when attacking from behind")

### Condition Combinations

Conditions can be combined to create complex requirements. Examples:

1. **Damage with Cooldown**:

   ```json
   "conditions": [
     {
       "type": "trigger",
       "trigger": "on_attack",
       "text": "your attacks"
     },
     {
       "type": "cooldown",
       "cooldown": 20.0,
       "text": "cannot occur more often than once every 20 seconds"
     }
   ]
   ```

   Effect only triggers on attacks, but no more than once every 20 seconds.

2. **Health-Based with State**:

   ```json
   "conditions": [
     {
       "type": "state",
       "state": "health_threshold",
       "text": "below 50% Life",
       "threshold": 50.0
     },
     {
       "type": "state",
       "state": "in_combat",
       "text": "while in combat"
     }
   ]
   ```

   Effect only active when below 50% health and in combat.

3. **Distance with Trigger**:

   ```json
   "conditions": [
     {
       "type": "distance",
       "distance": 8.0,
       "text": "at 8 yards"
     },
     {
       "type": "trigger",
       "trigger": "on_attack",
       "text": "your attacks"
     }
   ]
   ```

   Effect applies to attacks made at 8 yards range.

### Empty Conditions Array

An empty conditions array `[]` means the stat boost is:

- Always active
- No requirements to trigger
- No cooldown restrictions
- No state dependencies

Example of unconditional boost:

```json
{
  "conditions": [],
  "value": 5.0,
  "unit": "percentage",
  "scaling": false
}
```

This 5% boost is always active with no conditions.

## Value Properties

- `value`: Numerical value of the stat boost
- `unit`: Type of value
  - `percentage`: Percentage increase/decrease
  - `flat`: Flat numerical boost
- `scaling`: Boolean indicating if the value scales with conditions
- `conditions`: Array of conditions that must be met

## Usage Examples

### Example 1: Mother's Lament

```json
{
  "name": "Mother's Lament",
  "stars": "2",
  "base_values": [
    {
      "conditions": [
        {
          "type": "cooldown",
          "cooldown": 20.0,
          "text": "cannot occur more often than once every 20 seconds"
        }
      ],
      "value": 12.0,
      "unit": "percentage",
      "scaling": false
    }
  ],
  "rank_10_values": [
    {
      "conditions": [
        {
          "type": "state",
          "state": "health_threshold",
          "text": "below 50% Life",
          "threshold": 50.0
        }
      ],
      "value": 20.0,
      "unit": "percentage",
      "scaling": false
    }
  ]
}
```

This example shows:

1. Base value with cooldown restriction
2. Rank 10 value with health threshold condition
3. Non-scaling percentage values

### Detailed Example: Mother's Lament

This example shows how conditions, stats, and effects interact in a more detailed example of a gem:

```json
{
  "name": "Mother's Lament",
  "stars": "2",
  "base_values": [
    {
      "conditions": [
        {
          "type": "cooldown",
          "cooldown": 20.0,
          "text": "cannot occur more often than once every 20 seconds"
        }
      ],
      "value": 12.0,
      "unit": "percentage",
      "scaling": false
    }
  ],
  "rank_10_values": [
    {
      "conditions": [
        {
          "type": "trigger",
          "trigger": "on_damage_taken",
          "text": "Taking damage"
        }
      ],
      "value": 20.0,
      "unit": "percentage",
      "scaling": false
    }
  ]
}
```

This gem demonstrates several key concepts:

1. **Base Values (Rank 1)**:
   - Has a cooldown condition (20 seconds)
   - 20% chance to gain Maternal Disdain
   - Provides 12% critical hit chance for 6 seconds
   - Non-scaling value

2. **Rank 10 Values**:
   - Triggers on taking damage
   - Increases to 20% critical hit chance
   - Adds blood spike effect (300% base damage)
   - Adds bleed effect (50% base damage over 5s)

3. **State Management**:
   - Tracks "Maternal Disdain" buff state
   - Duration: 6 seconds
   - Rank 1: Random proc with cooldown
   - Rank 10: Guaranteed on taking damage
   - Ends with blood spike effect

4. **Multiple Stats Affected**:
   - Critical Hit Chance (primary stat)
   - Damage (from blood spike)
   - Damage over Time (from bleed)

This shows how a single gem can combine:

- Different condition types (cooldown vs trigger)
- State tracking (buff management)
- Multiple effects (buff, damage, DoT)
- Different trigger mechanics at rank 1 vs rank 10

## Implementation Notes

1. **Text Fields**: Used for UI display and pattern matching
   - More specific than regex patterns (e.g., "below 50% Life" vs "below (\\d+)% (?:life|health)")
   - Maintains readability while ensuring accurate matching

2. **Conditions Array**: Can be empty or contain multiple conditions
   - Empty array = unconditional boost
   - Multiple conditions = all must be met

3. **Value Types**:
   - Percentage values are stored as decimals (e.g., 12.0 = 12%)
   - Cooldowns are in seconds
   - Thresholds are in their natural unit (percentages for health, etc)

## Best Practices

1. **Adding New Gems**:
   - Include all conditions that affect the stat
   - Provide clear, specific text descriptions
   - Include both base and rank 10 values
   - Specify all relevant conditions

2. **Updating Existing Gems**:
   - Maintain the same structure
   - Update all affected fields
   - Keep text descriptions consistent

3. **Version Control**:
   - Update metadata version when making structural changes
   - Document significant changes in commit messages

## Related Systems

This file is used in conjunction with:

- Build optimization algorithms
- Stat calculation systems
- UI display systems
- Game balance analysis tools
