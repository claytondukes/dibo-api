# Gem System

## Overview

The gem system in Diablo Immortal consists of two main types:

1. Legendary Gems - Powerful gems that provide unique effects and resonance
2. Normal Gems - See [Secondary Gems](secondary_gems.md) for details

## Legendary Gems

### Star Ratings

- 1★ Gems: Basic legendary effects
- 2★ Gems: Intermediate effects and resonance
- 5★ Gems: Most powerful effects and highest resonance

### Categories by Effect Type

#### Movement-Based

- **Blood-Soaked Jade** (5★)
  - Base: Up to 8% damage at full life, +10% Movement Speed
  - Rank 10: Up to 32% damage, +20% Movement Speed, life steal
  
- **Lightning Core** (2★)
  - Base: Primary Attacks charge lightning chain
  - Rank 10: Enhanced chain lightning + crit chance

#### Primary Attack

- **Ca'arsen's Invigoration** (1★)
  - Effect: Increases Primary Attack speed

#### Defensive

- **Blessing of the Worthy** (5★)
  - Effect: Chance to unleash retribution when taking damage
  - Provides damage reduction

### Progression System

Each gem can be upgraded through ranks:

- Higher ranks increase effect potency
- Unlocks additional effects
- Increases Combat Rating contribution
- Enhances resonance (2★ and 5★ gems)

### Resonance System

- Only 2★ and 5★ gems provide resonance
- Resonance multiplies base attributes
- Higher gem ranks provide more resonance
- 5★ gems provide the highest resonance per rank

### Auxiliary System

See [Auxiliary Gems](aux_gems.md) for details about:

- Auxiliary gem mechanics
- Effect combinations
- Optimization strategies

## Normal Gems

See [Secondary Gems](secondary_gems.md) for comprehensive documentation of the normal gem system.

## Data Structure

### Static Data (in indexed/)

Located in `data/indexed/gems/`:

1. `gems.json`:
   - Gem definitions
   - Base effects
   - Star ratings
   - Categories

2. `progression.json`:
   - Rank requirements
   - Effect scaling
   - Resonance values

3. `stat_boosts.json`:
   - Stat modifications
   - Scaling factors
   - Combat rating contributions

4. `synergies.json`:
   - Gem combinations
   - Build synergies
   - Optimization data

### Dynamic Data (in GitHub Gists)

Player-specific gem data includes:

- Owned gems and ranks
- Socket assignments
- Resonance totals
- Auxiliary configurations

## API Implementation Notes

When implementing gem-related endpoints:

1. Query available gems from indexed data
2. Calculate progression requirements
3. Handle gem ranking system
4. Process resonance calculations
5. Manage socket assignments
6. Consider build synergies
7. Track auxiliary configurations
8. Calculate total stat contributions
