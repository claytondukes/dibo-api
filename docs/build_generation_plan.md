# Build Generation Implementation Plan

## Overview

This document outlines the implementation plan for DIBO's build generation system. The system will generate optimized character builds based on user preferences, game mechanics, and optionally their existing inventory.

## Current Implementation Status

### Implemented Components:

1. API Structure:
   - `/builds/generate` endpoint defined
   - Request/response models
   - Basic service structure

2. Data Management:
   - Data loading system
   - File validation
   - Data structure verification

3. Core Features:
   - Basic gem selection algorithm
   - Inventory validation
   - GitHub Gist integration
   - Advanced essence scoring system
   - Build type specific scoring
   - Percentage bonus handling
   - Attack speed modifiers

### Missing/Incomplete Components:

1. Core Selection Algorithms:
   - `_select_skills`: Control/buff validation
   - `_select_equipment`: Equipment selection system
   - `_calculate_stats`: Stats aggregation
   - `_find_synergies`: Synergy detection
   - `_calculate_equipment_score`: Equipment scoring
   - `_calculate_set_score`: Set bonus evaluation

2. Analysis Systems:
   - Synergy analysis
   - Stats calculation
   - Equipment optimization
   - Set piece combinations

### Implementation Status:

```
✅ Complete
- Data loading and validation
- Basic gem selection
- Inventory validation
- API endpoint structure
- GitHub Gist integration
- Gem synergy scoring
- Basic skill scoring
- DPS focus essence scoring
- Percentage bonus scoring
- RAID build scoring
- Attack speed modifiers

🚧 In Progress
- Control/buff skill validation
- Equipment selection (stub)
- Stats calculation (stub)

❌ Not Started
- Set piece optimization
- Equipment scoring
- Build recommendations
- Integration testing
```

## Core Components

### 1. Build Generation Pipeline

```mermaid
graph TD
    A[User Request] --> B[Validate Input]
    B --> C[Load Data]
    C --> D[Select Gems]
    D --> E[Select Skills]
    E --> F[Select Equipment]
    F --> G[Calculate Stats]
    G --> H[Find Synergies]
    H --> I[Generate Recommendations]
    I --> J[Return Build]
```

### 2. Data Models

#### Request Model
```python
class BuildRequest:
    build_type: BuildType      # raid, pve, pvp, farm
    focus: BuildFocus         # dps, survival, buff
    character_class: str      # e.g., "barbarian"
    use_inventory: bool = False
```

#### Response Model
```python
class BuildResponse:
    build: BuildRecommendation
    stats: BuildStats
    recommendations: List[str]
```

## Implementation Phases

### Phase 1: Core Selection Algorithms

1. Skill Selection (`_select_skills`)
   - Input: build type, focus, selected gems
   - Algorithm:
     1. Filter skills by character class
     2. Score each skill based on:
        - Base effectiveness for build type
        - Synergy with selected gems
        - Focus alignment (e.g., DPS vs Survival)
        - Percentage-based improvements
        - Attack speed modifiers
     3. Select optimal skill combination
     4. Validate against class constraints
     5. Verify control/buff requirements

2. Equipment Selection (`_select_equipment`)
   - Input: build type, focus, gems, skills
   - Algorithm:
     1. Score equipment pieces based on:
        - Base stats alignment with focus
        - Synergies with gems and skills
        - Set bonuses potential
     2. Optimize set combinations
     3. Fill remaining slots with best-in-slot items

### Phase 2: Stats and Synergies

1. Stats Calculation (`_calculate_stats`)
   - Implement stat aggregation from:
     - Base stats
     - Gem bonuses
     - Equipment bonuses
     - Set bonuses
     - Skill modifiers
   - Calculate derived stats:
     - DPS metrics
     - Survival metrics
     - Utility metrics

2. Synergy Analysis (`_find_synergies`)
   - Implement synergy detection:
     - Gem-to-gem synergies
     - Gem-to-skill synergies
     - Skill-to-skill synergies
     - Equipment set synergies
   - Score synergy effectiveness
   - Identify anti-synergies

### Phase 3: Scoring Systems

1. Skill Scoring (`_calculate_skill_score`) 
   - Base score calculation based on skill type and build focus
   - Focus multiplier for build type alignment
   - Gem synergy bonus calculation
   - Cooldown impact consideration
   - Type-specific bonuses (control, mobility)
   - Percentage-based effect bonuses
   - Attack speed modifier bonuses
   - RAID-specific optimizations

2. Equipment Scoring (`_calculate_equipment_score`)
   ```python
   def _calculate_equipment_score(item, build, focus):
       stat_score = score_stats_alignment(item, focus)
       synergy_score = score_synergies(item, build)
       set_potential = evaluate_set_potential(item)
       return (stat_score * 0.4 + 
               synergy_score * 0.4 + 
               set_potential * 0.2)
   ```

3. Set Scoring (`_calculate_set_score`)
   ```python
   def _calculate_set_score(set_name, build):
       bonus_score = score_set_bonuses(set_name, build)
       synergy_score = score_set_synergies(set_name, build)
       return (bonus_score * 0.6 + synergy_score * 0.4)
   ```

### Phase 4: Optimization and Constraints

1. Build Constraints
   - Implement constraint checking:
     - Skill slot limits
     - Gem star rating compatibility
     - Equipment slot restrictions
     - Set piece combinations
     - Control/buff requirements
     - Mobility skill requirements

2. Build Optimization
   - Implement optimization strategies:
     - Set piece combination optimization
     - Gem slot allocation optimization
     - Skill loadout optimization
     - Equipment stat priority optimization
     - Build type specific optimizations
     - Percentage bonus maximization

### Phase 5: Inventory Integration

1. Inventory Adaptation
   - Modify selection algorithms to consider:
     - Available gems and their ranks
     - Available equipment pieces
     - Existing set combinations
     - Current skill loadout

2. Inventory Optimization
   - Implement inventory-aware optimization:
     - Maximize use of existing high-value items
     - Suggest minimal changes for improvement
     - Consider upgrade paths
     - Balance immediate vs long-term goals

## Next Steps

1. Fix remaining skill validation issues:
   - Improve control/buff skill detection
   - Fix integration test failures
   - Add more test coverage for edge cases

2. Begin equipment selection implementation:
   - Design scoring system for equipment
   - Implement set bonus evaluation
   - Add inventory integration

3. Enhance build optimization:
   - Add more build type specific logic
   - Implement advanced synergy detection
   - Improve recommendation generation
