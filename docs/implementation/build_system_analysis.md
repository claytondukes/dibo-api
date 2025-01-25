# Diablo Immortal Build System Analysis Guide

## 1. Core System Components

### 1.1 Equipment Structure

- **Primary Gear (6 slots)**
  - Head
  - Shoulders
  - Chest
  - Legs
  - Main Hand
  - Off-Hand
  - Each slot can hold one essence modification

- **Set Items (8 slots)**
  - Neck
  - Waist
  - Hands
  - Feet
  - 2x Rings
  - 2x Bracers
  - Can form set combinations: 6+2, 4+4, 4+2+2, or 2+2+2+2

### 1.2 Gem System

- **Total Required: 8 gems**
- **Star Rating Distribution:**
  - Must include 1★, 2★, and 5★ gems
  - Each gem must be unique
- **Primary/Auxiliary System:**
  - Primary gems provide resonance and stats
  - Auxiliary gems must match primary star rating
  - Cannot duplicate gems between primary/aux slots

### 1.3 Skills System

- **Skill Slots:**
  - 4 active skill slots
  - 1 weapon skill slot (e.g., Lacerate, Frenzy)
- **Base Skills:**
  - Listed in base_skills.json
  - Represent unmodified skill behavior
  - Categories: damage, control, buff, dash
  - Secondary types: multiple-stage, charge, channel

### 1.4 Essence System

- **Purpose:** Modifies skill behavior
- **Data Structure:**
  - Organized by class and slot
  - Each slot has dedicated essence file
  - Metadata describes skills and mechanics
  - Indexes for efficient lookup
- **Constraints:**
  - One essence per primary gear slot
  - Must modify an equipped skill to be useful
  - Specific essences tied to specific slots
- **Effect Types:**
  - Damage: Direct increases, new effects
  - Utility: Cooldowns, resources, control
  - Defense: Mitigation, healing, shields

## 2. Data Analysis Process

### 2.1 Build Foundation

1. **Analyze Available Data**
   - Review class-specific essence files
   - Check essence counts by slot
   - Map available modifications and synergies

2. **Skill Selection**
   - Choose weapon skill first
   - Select 4 active skills that:
     - Have essence options in multiple slots
     - Cover necessary functions (damage/control/mobility)
     - Work together mechanically

3. **Essence Mapping**
   - Use by_slot.json for slot availability
   - Use by_skill.json for skill modifications
   - Use by_effect.json for effect types
   - Consider essence effect synergies

### 2.2 Build Optimization

1. **Set Selection**
   - Analyze set bonuses against build goals
   - Consider skill type synergies
   - Account for content type (PvP/PvE)
   - Check valid set combinations

2. **Gem Configuration**
   - Meet star rating requirements
   - Maximize resonance within constraints
   - Consider gem effect synergies
   - Plan primary/auxiliary combinations

3. **Synergy Analysis**
   - Map all possible interactions between:
     - Skill effects
     - Essence modifications
     - Set bonuses
     - Gem effects
   - Identify multiplicative damage sources
   - Consider crowd control chains
   - Evaluate survival mechanisms

## 3. Decision Making Logic

### 3.1 Build Type Determination

1. **Content Focus**
   - PvP: Control, burst, survival
   - PvE: Sustained damage, AoE clear
   - Raid: Single target, survival
   - Farm: Speed, efficiency, synergies

2. **Required Functions**
   - Damage output
   - Crowd control
   - Mobility
   - Survival mechanics
   - Team utility

### 3.2 Skill Selection Logic

1. **Map Available Essences**

   ```python
   def map_essence_coverage():
       essence_map = {}
       for skill in skills:
           essence_map[skill] = {
               slot: [] for slot in gear_slots
           }
           for essence in essences:
               if essence.modifies_skill == skill:
                   essence_map[skill][essence.slot].append(essence)
       return essence_map
   ```

2. **Evaluate Skill Combinations**

   ```python
   def evaluate_skill_combo(skills):
       covered_slots = set()
       for skill in skills:
           for slot in gear_slots:
               if essence_map[skill][slot]:
                   covered_slots.add(slot)
       return len(covered_slots) == 6
   ```

### 3.3 Synergy Evaluation

1. **Effect Stacking**
   - Additive vs multiplicative bonuses
   - Duration overlaps
   - Condition triggers
   - Cooldown alignment

2. **Mechanical Interactions**

   ```python
   def evaluate_synergy(build):
       score = 0
       score += evaluate_damage_synergy()
       score += evaluate_control_synergy()
       score += evaluate_survival_synergy()
       score += evaluate_utility_synergy()
       return score
   ```

## 4. Implementation Steps

### 4.1 Build Creation Process

1. **Initialize Build**
   - Select content type
   - Define required functions
   - Set target metrics

2. **Skill Selection**

   ```python
   def select_skills():
       weapon_skill = select_weapon_skill()
       active_skills = []
       
       # Find skills with good essence coverage
       potential_skills = get_skills_with_essence_coverage()
       
       # Select complementary skills
       while len(active_skills) < 4:
           best_skill = evaluate_next_best_skill(active_skills)
           active_skills.append(best_skill)
           
       return weapon_skill, active_skills
   ```

3. **Essence Assignment**

   ```python
   def assign_essences(skills):
       assignments = {}
       for slot in gear_slots:
           best_essence = find_best_essence_for_slot(
               slot, skills, assignments
           )
           assignments[slot] = best_essence
       return assignments
   ```

### 4.2 Build Validation

1. **Check Constraints**
   - Verify skill count
   - Confirm essence coverage
   - Validate gem distribution
   - Check set combinations

2. **Verify Synergies**
   - Confirm mechanical interactions
   - Check cooldown alignments
   - Validate damage patterns
   - Assess survival mechanisms

## 5. Common Pitfalls

1. **Build Creation**
   - Selecting skills without essence coverage
   - Ignoring weapon skill modifications
   - Mismatching gear slot essences
   - Incomplete slot utilization

2. **System Understanding**
   - Confusing base skills with modifications
   - Overlooking weapon skill options
   - Missing cross-skill synergies
   - Ignoring content-specific requirements

## 6. Best Practices

1. **Data Handling**
   - Always verify against source files
   - Check all possible modifications
   - Consider all slot options
   - Validate assumptions

2. **Build Development**
   - Start with weapon skill
   - Ensure full slot utilization
   - Maximize synergies
   - Consider build versatility

3. **Validation Process**
   - Check all constraints
   - Verify mechanical interactions
   - Test alternate configurations
   - Consider edge cases

## Build System Analysis

### Overview

The build system is responsible for generating and analyzing character builds based on various inputs and constraints. It integrates with the equipment, gem, and skill systems to create optimized character configurations.

### Core Components

#### 1. Build Service

The `BuildService` class is the central component that:

- Manages data loading and validation
- Generates build recommendations
- Analyzes build performance
- Handles class-specific constraints

```python
class BuildService:
    """Service for generating and analyzing builds."""
    
    REQUIRED_FILES = {
        # Core data files
        "build_types": "build_types.json",
        "stats": "gems/stat_boosts.json",
        "constraints": "constraints.json",
        "synergies": "synergies.json",
        
        # Gem-related files
        "gems/skillmap": "gems/gem_skillmap.json",
        "gems/data": "gems/gems.json",
        "gems/stat_boosts": "gems/stat_boosts.json",
        "gems/synergies": "gems/synergies.json",
        
        # Equipment data
        "sets": "sets.json",
        
        # Class-specific data
        "classes/{class}/essences": "classes/{class}/essences.json"
    }
```

#### 2. Data Models

##### Build Types

```python
class BuildType(str, Enum):
    """Build type enumeration."""
    RAID = "raid"
    FARM = "farm"
    PVP = "pvp"
```

##### Build Focus

```python
class BuildFocus(str, Enum):
    """Primary focus of the build."""
    DPS = "dps"
    SURVIVAL = "survival"
    BUFF = "buff"
```

##### Component Models

- `Gem`: Gem configuration with rank and quality
- `Skill`: Skill configuration with optional essence
- `Equipment`: Equipment configuration with attributes and essence
- `BuildStats`: Performance metrics (DPS, survival, utility)
- `BuildRecommendation`: Complete build configuration
- `BuildResponse`: Full response including stats and URLs

### Data Flow

1. **Initialization**

   ```python
   @classmethod
   async def create(cls, data_dir: Optional[Path] = None) -> 'BuildService':
       instance = cls(data_dir)
       await instance.initialize()
       return instance
   ```

2. **Data Loading**
   - Core data (build types, constraints)
   - Set bonuses
   - Gem data (skills, stats, synergies)
   - Class-specific data (essences, base skills)

3. **Build Generation**
   - Input validation
   - Constraint checking
   - Equipment selection
   - Gem optimization
   - Skill configuration
   - Performance analysis

### Key Features

#### 1. Equipment Integration

- Supports both gear slots and set slots
- Handles weapon swap mechanics
- Integrates with essence system
- Validates slot constraints

#### 2. Build Analysis

- DPS calculation
- Survival metrics
- Utility scoring
- Synergy detection
- Constraint validation

#### 3. Recommendations

- Equipment suggestions
- Gem combinations
- Skill configurations
- Set bonus optimization
- Alternative builds

### Performance Considerations

#### 1. Data Management

- Efficient caching through GameDataManager
- Lazy loading of class-specific data
- Memory-optimized data structures

#### 2. Computation

- Score-based build ranking
- Efficient constraint checking
- Parallelized calculations where possible
- Caching of intermediate results

#### 3. Response Time

- Asynchronous data loading
- Optimized build generation
- Efficient JSON serialization

### Testing Strategy

#### 1. Unit Tests

- Build generation logic
- Score calculation
- Constraint validation
- Data loading

#### 2. Integration Tests

- Equipment integration
- Gem system interaction
- Skill configuration
- Full build generation

#### 3. Performance Tests

- Response time benchmarks
- Memory usage monitoring
- Cache effectiveness
- Load testing

### Error Handling

#### 1. Data Validation

```python
def _validate_data_structure(self) -> None:
    """Validate loaded data structure."""
    # Validate build types
    if not self.build_types:
        raise ValueError("No build types defined")
        
    # Validate constraints
    if not self.constraints:
        raise ValueError("No constraints defined")
        
    # Validate class data
    for class_name in self.CHARACTER_CLASSES:
        if class_name not in self.class_data:
            raise ValueError(f"Missing data for class: {class_name}")
```

#### 2. Runtime Errors

- Invalid build requests
- Missing data
- Constraint violations
- Performance issues

#### 3. Response Format

```python
{
    "error": str,
    "detail": str,
    "context": Optional[Dict],
    "suggestions": List[str]
}
```

### Future Improvements

1. **Build Optimization**
   - Enhanced scoring algorithms
   - Machine learning integration
   - Historical build analysis

2. **Performance**
   - Improved caching strategies
   - Parallel build generation
   - Optimized constraint checking

3. **Features**
   - Build comparison
   - Build history
   - Build sharing
   - Dynamic build generation (replacing static templates)
   - Build optimization based on game dynamics

### TODO: Resonance Integration

#### Build Generation Considerations

Resonance importance varies by content type:

1. **High Priority**
   - Challenge Rifts
     - Total resonance directly impacts clear potential
     - Consider minimum resonance thresholds for target levels
   - Raids
     - Required resonance thresholds for different difficulties
     - Balance between resonance and specific boss mechanics
   - PvP
     - Resonance affects matchmaking brackets
     - Consider impact when using aux gems (trading resonance for effects)

2. **Medium Priority**
   - General PvE
     - Resonance helps with damage output
     - Less important than synergistic gem properties
   - Farming
     - Prioritize proc effects and synergies
     - Lower star gems may outperform higher resonance
     - Example: 2-star gem with strong proc > 5-star with just resonance
     - Focus on:
       - Clear speed mechanics
       - AoE damage potential
       - Proc frequency
       - Build synergies
       - Movement speed
     - Resonance considered last after all synergies

#### Implementation Tasks

1. Add resonance calculation to build scoring:

   ```python
   def calculate_build_score(build: Build) -> float:
       base_score = calculate_base_score(build)
       
       # Get content-specific weights
       resonance_weight = get_resonance_weight(build.content_type)
       synergy_weight = get_synergy_weight(build.content_type)
       
       # Calculate scores
       resonance_score = calculate_resonance_score(build.gems)
       synergy_score = calculate_synergy_score(build)
       
       # For farming, prioritize synergies
       if build.content_type == ContentType.FARMING:
           return base_score * (
               1 + 
               (synergy_score * synergy_weight) +
               (resonance_score * resonance_weight * 0.1)  # Reduced resonance impact
           )
       
       # For other content types
       return base_score * (
           1 + 
           (resonance_score * resonance_weight) +
           (synergy_score * synergy_weight)
       )
   ```

2. Add content-specific resonance thresholds:

   ```python
   RESONANCE_THRESHOLDS = {
       ContentType.CHALLENGE_RIFT: {
           "tier_70": 1000,
           "tier_100": 2000,
           # Add more tiers
       },
       ContentType.RAID: {
           "normal": 500,
           "hell_1": 1000,
           # Add more difficulties
       },
       ContentType.FARMING: {
           # No strict thresholds
           # Focus on synergy scores instead
           "recommended": 0  # Any resonance acceptable
       }
   }
   ```

3. Consider aux gem tradeoffs:
   - Track both primary and aux configurations
   - Calculate effective power loss from aux substitution
   - Weight against gained utility/effects
   - For farming:
     - Prioritize proc effects and synergies
     - Consider downgrading to lower star gems for better effects
     - Calculate effective clear speed impact

4. Add resonance validation:
   - Verify builds meet minimum requirements
   - Warning for suboptimal resonance configurations
   - Suggestions for resonance improvements
   - For farming builds:
     - Focus validation on synergies
     - Only warn about resonance if extremely low
     - Suggest gem alternatives based on effects
