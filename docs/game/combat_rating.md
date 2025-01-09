# Combat Rating System

## Overview

Combat Rating (CR) is a critical metric in Diablo Immortal that determines a character's effectiveness, particularly in endgame content like Challenge Rifts and raids. It's a numerical value that represents overall power level, derived from various sources including gear, gems, and resonance.

## Importance

- Primary factor for success in Challenge Rifts
- Critical for raid participation and effectiveness
- More important than skill combinations or set bonuses in certain content
- Used for content gating and difficulty scaling

## Sources of Combat Rating

### 1. Gear

- Base item level
- Attribute values
- Quality/rank of items

### 2. Gems

- Legendary Gems provide significant CR
- Normal Gems contribute based on rank
- See [Gems](gems.md) for details about resonance calculations

### 3. Helliquary

- Boss kills increase CR
- Scoria upgrades

### 4. Other Sources

- Paragon levels
- Challenge Rift completions
- Horadric Vessel upgrades

## Impact on Gameplay

### Challenge Rifts

- CR is the primary determinant of success
- Higher CR allows access to higher rift levels
- CR differences create damage penalties/bonuses

### Raids

- Minimum CR requirements for participation
- Higher CR increases individual effectiveness
- Affects damage dealt and taken

### PvE Content

- Affects damage dealt and taken
- Influences difficulty scaling
- Required for certain content thresholds

## CR Breakpoints

Important CR thresholds for various content types:

- Challenge Rift progression
- Raid participation
- Hell difficulty levels

## API Implementation Notes

When calculating CR:

1. Sum base CR from all gear pieces
2. Add CR from socketed gems
3. Include CR from other sources
4. Consider CR requirements for content recommendations
