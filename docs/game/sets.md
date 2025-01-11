# Equipment Sets

## Overview

Equipment sets are collections of gear pieces that provide additional bonuses when multiple pieces from the same set are equipped. Sets are class-agnostic, meaning any class can equip and benefit from any set.

## Set Bonuses

Sets provide bonuses at specific thresholds:

- 2-piece bonus: Basic set bonus
- 4-piece bonus: Intermediate set bonus
- 6-piece bonus: Powerful set bonus

Bonuses are cumulative, meaning if you have 6 pieces equipped, you get all three bonuses (2-piece, 4-piece, and 6-piece).

## Example Set

Here's an example of the "Grace of the Flagellant" set:

```json
{
  "pieces": 6,
  "description": "A set focused on DoT, channeled, and AoE damage builds.",
  "bonuses": {
    "2": "Increases all continual, channeled, and persistent ground damage by 15%.",
    "4": "Each time you damage an individual enemy 5 times, you deal additional damage to that enemy.",
    "6": "Each time you deal damage, you have a chance to unleash a lightning strike, dealing AoE damage and stunning enemies."
  },
  "use_case": "Best for DoT, channeled, or AoE damage builds."
}
```

## Set Pieces

Each set consists of pieces that can be equipped in different slots:

### Right Side (Gear Slots)

- Head (Helm)
- Shoulders
- Chest (Torso armor)
- Legs
- Main Hand (Set 1) - Primary weapon
- Off-Hand (Set 1) - Shield or off-hand weapon
- Main Hand (Set 2) - Secondary weapon set
- Off-Hand (Set 2) - Secondary shield/weapon

### Left Side (Set Slots)

- Neck (Necklace)
- Waist (Belt)
- Hands (Gloves)
- Feet (Boots)
- Ring 1
- Ring 2
- Bracer 1
- Bracer 2

## Implementation Details

Sets are defined in `data/indexed/sets.json` with the following structure:

```json
{
  "metadata": {
    "bonus_thresholds": [2, 4, 6],
    "bonus_rules": "Set bonuses are additive..."
  },
  "registry": {
    "SetName": {
      "pieces": <total_pieces>,
      "description": <set_description>,
      "bonuses": {
        "2": <2_piece_bonus>,
        "4": <4_piece_bonus>,
        "6": <6_piece_bonus>
      },
      "use_case": <recommended_usage>
    }
  }
}
```

## Build Considerations

When generating builds, the following factors are considered for set selection:

1. Build Type (PvE, PvP, Raid, Farm)
2. Build Focus (damage, survival, utility)
3. Synergies with:
   - Selected gems
   - Selected skills
   - Essence modifications

## Common Set Types

Sets generally fall into these categories:

1. **Damage Sets**
   - Direct damage increase
   - Critical hit focused
   - Attack speed focused
   - DoT/Channeled damage

2. **Defensive Sets**
   - Armor/Resistance increase
   - Block/Dodge chance
   - Health/Resource regeneration
   - Damage reduction

3. **Utility Sets**
   - Resource generation
   - Cooldown reduction
   - Movement speed
   - Gold/item finding

4. **Hybrid Sets**
   - Combinations of the above
   - Situational bonuses
   - Conditional effects
