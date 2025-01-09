# Diablo Immortal Build System Analysis Guide

## 1. Core System Components

### 1.1 Equipment Structure

- **Primary Gear (8 slots)**
  - Head
  - Shoulders
  - Chest
  - Legs
  - Main Hand (Set 1)
  - Off-Hand (Set 1)
  - Main Hand (Set 2)
  - Off-Hand (Set 2)
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
- **Constraints:**
  - One essence per primary gear slot
  - Must modify an equipped skill to be useful
  - Specific essences tied to specific slots

## 2. Data Analysis Process

### 2.1 Build Foundation

1. **Analyze Available Data**
   - Review all JSON files for complete picture
   - Check constraints.json for system limits
   - Map available modifications and synergies

2. **Skill Selection**
   - Choose weapon skill first
   - Select 4 active skills that:
     - Have essence options in multiple slots
     - Cover necessary functions (damage/control/mobility)
     - Work together mechanically

3. **Essence Mapping**
   - List all available essences by slot
   - Map which skills have essences in which slots
   - Ensure chosen skills can utilize all 8 gear slots
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
   - Farm: Speed, efficiency

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
       return len(covered_slots) == 8
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
