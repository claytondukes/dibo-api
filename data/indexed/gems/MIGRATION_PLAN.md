# Gem System Migration Plan

Last Updated: 2025-01-13T09:26:43-05:00

## Overview

This document outlines the steps needed to update the API to work with the new modular gem data structure. The recent refactoring split monolithic JSON files into individual files for better maintainability.

## Current Changes

### Directory Structure Changes

```text
data/indexed/gems/
├── core/                # Individual gem files
│   ├── 1star/          # 1-star gems
│   ├── 2star/          # 2-star gems
│   └── 5star/          # 5-star gems
├── metadata/           # Shared data files
│   ├── synergies/      # Synergy-related data
│   │   ├── core/       # Core synergy definitions
│   │   │   ├── synergy_weights.json
│   │   │   └── build_types.json
│   │   ├── categories.json
│   │   └── gem_pairs.json
│   ├── skillmap/       # Skill mapping data
│   └── stat_boosts/    # Stat boost data
└── index.json         # Gem path mapping
```

### Completed Changes

- Split `gems.json` into individual gem files
- Moved skillmap data to metadata directory
- Moved stat boosts to dedicated directory
- Created synergy metadata structure
- Updated gem categories and pairs
- Implemented core synergy weights
- Created build type definitions

### Known Issues

1. Effect Documentation:
   - Document which effects should have empty conditions arrays (passive effects)
   - Add explicit "passive" condition type for always-active effects

2. API Updates Required:
   - GameDataManager still using old monolithic file paths
   - Need to implement modular file loading
   - Update caching strategy for individual files

## Implementation Plan

### Phase 1: Data Validation 

1. Verify all gem files are properly split and located
2. Check for missing rank information
3. Validate effect data correctness
4. Ensure conditions are properly mapped

### Phase 2: API Updates (In Progress)

1. Update GameDataManager (api/models/game_data/manager.py):
   - Modify file path handling for new structure
   - Update data loading logic for individual files
   - Implement efficient caching for modular files

2. Update BuildService (api/builds/service.py):
   - Remove hardcoded file paths
   - Update gem loading logic
   - Modify synergy calculations for new structure

3. Update Synergy Handling:
   - Implement new metadata directory structure
   - Update synergy calculations
   - Fix condition mapping

### Phase 3: Testing

1. Verify Data Loading:
   - Test loading all individual gem files
   - Validate metadata loading
   - Check synergy calculations

2. Performance Testing:
   - Measure load times with new structure
   - Test caching effectiveness
   - Monitor memory usage

## Validation Checklist

- [x] All gem files properly located in core/{1,2,5}star/
- [x] Metadata files correctly structured
- [ ] GameDataManager updated for new paths
- [ ] BuildService modified for individual files
- [x] Missing rank data documented in [gems.md](../docs/game/gems.md#rank-data-coverage)
- [ ] Incorrect effects fixed
- [ ] All tests passing

## Next Steps

1. Document missing rank information
2. Fix incorrect effect data
3. Update API code for new structure
4. Add comprehensive tests
5. Monitor performance impact
