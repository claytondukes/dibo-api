# Paragon System

## Overview

The Paragon system provides post-max-level character progression in Diablo Immortal.

## TODO Items

### Research Needed

- [ ] Document paragon tree structure
- [ ] List all paragon paths and their effects
- [ ] Document how paragon levels affect CR
- [ ] Explain server paragon level system
- [ ] Document XP catch-up mechanics
- [ ] List level-gated content/features
- [ ] Document paragon prestige system

### Implementation Questions

1. How should paragon tree choices be stored in player data?
2. What's the best way to calculate effective paragon level considering server level?
3. How do we handle paragon respecs?
4. How should we represent paragon bonuses in build calculations?
5. What's the interaction between paragon choices and set bonuses?
6. How do paragon attributes affect CR calculations?

### Data Structure Needs

- Paragon tree layout
- Node effects and requirements
- Path-specific bonuses
- Level-based stat increases
- Prestige system details

## Current Understanding

Basic system components that we know:

1. Multiple specialization paths
2. Server paragon level system
3. Catch-up XP mechanics
4. Level-based stat increases
5. Respec capability

## API Considerations

When implementing paragon-related features:

1. Need to track individual player progress
2. Consider server paragon level
3. Handle respec scenarios
4. Calculate effective bonuses
5. Integrate with build recommendations
