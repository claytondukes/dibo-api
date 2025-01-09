# Gear System

## Overview

The gear system in Diablo Immortal consists of two distinct categories:

1. Normal (Primary) Gear - Core equipment with legendary effects
2. Set Items - Special gear that provides set bonuses

## Normal Gear

Normal gear pieces are the main equipment slots that can have multiple modifications:

- Legendary effects that modify skills
- Legendary gem sockets
- Rune sockets for attribute bonuses
- Magic effects and properties

### Normal Gear Slots (8 total)

```text
Character Right Side:
┌─────────┬──────────┐
│  Head   │  Chest   │
├─────────┼──────────┤
│Shoulders│   Legs   │
├─────────┼──────────┤
│  Main   │   Off    │
│  Hand   │  Hand    │
├─────────┼──────────┤
│  Main   │   Off    │
│  Hand   │  Hand    │
└─────────┴──────────┘
```

1. Head - Helm slot
2. Chest - Torso armor
3. Shoulders - Shoulder armor
4. Legs - Leg armor
5. Main Hand (Set 1) - Primary weapon set 1
6. Off-Hand (Set 1) - Off-hand weapon/shield set 1
7. Main Hand (Set 2) - Primary weapon set 2
8. Off-Hand (Set 2) - Off-hand weapon/shield set 2

### Normal Gear Modifications

#### 1. Legendary Effects

- Each piece can have one legendary effect
- Modifies specific skill behavior
- Class-specific modifications
- Example: "Vortex Shout: Demoralize now pulls in all nearby enemies, dealing damage..."

#### 2. Legendary Gem Sockets

- One legendary gem socket per item
- Provides combat rating and special effects
- Example from game:

  ```text
  Blood-Soaked Jade (★★★★★)
  +2240 Combat Rating
  - Increases Resonance by 1115
  - Deal up to 24% while at full life
  - Additional bonus of 12% while at low life
  ```

#### 3. Rune Sockets

- Multiple rune slots available
- Provide attribute and stat bonuses
- Examples:
  - "Base attribute of equipped item increased by 8.0%"
  - "Damage taken while moving decreased by 3.0%"
  - "Attack Speed increased by 4.0%"
  - "Skill cooldowns reduced by 4.0%"

#### 4. Magic Effects

- Random magical properties
- Combat rating contributions
- Attribute boosts
- Special combat effects

## Set Items

Set items occupy different slots from normal gear and provide set bonuses when multiple pieces from the same set are equipped.

### Set Item Slots (8 total)

```text
Character Left Side:
┌────────┬─────────┐
│ Neck   │  Waist  │
├────────┼─────────┤
│ Hands  │  Feet   │
├────────┼─────────┤
│ Ring 1 │ Ring 2  │
├────────┼─────────┤
│Bracer 1│Bracer 2 │
└────────┴─────────┘
```

1. Neck - Necklace slot
2. Waist - Belt slot
3. Hands - Glove slot
4. Feet - Boot slot
5. Ring 1 - First ring slot
6. Ring 2 - Second ring slot
7. Bracer 1 - First bracer slot
8. Bracer 2 - Second bracer slot

### Set Item Modifications

#### 1. Normal Gem Sockets

- Can socket normal gems (not legendary)
- Available gem types:
  - Sapphire: Armor Penetration
  - Citrine
  - Ruby
  - Aquamarine
  - Topaz: Resistance
  - Tourmaline: Damage
- Examples from game:

  ```text
  Tourmaline (Rank 9): +380 Damage
  Topaz (Rank 8): +656 Resistance
  Sapphire (Rank 8): +656 Armor Penetration
  ```

#### 2. Set Properties

- Items belong to specific sets
- Set bonuses activate at piece thresholds (2/4/6)
- Example:

  ```text
  Vithu's Urges
  - Increases the duration of all beneficial effects
    on you or your party members by 30%.
  ```

#### 3. Magic Effects

- Random magical properties
- Examples:
  - Stun resistance increased by 4.0%
  - Movement speed increased by 3.0%
  - Damage taken from players reduced by 1.5%

## Core Attributes

All gear can contribute to core attributes:

- Willpower
- Strength
- Intelligence
- Wisdom
- Vitality

## Data Storage

### Static Data (in indexed/)

- Base item templates
- Possible legendary effects
- Gem definitions
- Set definitions
- Rune possibilities
- Possible magic properties

### Dynamic Data (in GitHub Gists)

Player-specific gear data including:

- Current attribute values
- Socketed gems and their ranks
- Applied runes
- Magic properties
- Combat rating

## API Considerations

When implementing gear-related endpoints:

1. Base templates and possibilities should come from indexed data
2. Actual gear stats should be pulled from player gists
3. Support querying both normal and set items
4. Allow filtering by modification types (gems, runes, effects)
5. Consider set bonus calculations
6. Handle combat rating calculations
