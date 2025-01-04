import json
from typing import Dict, Set, List
from pprint import pprint

def load_json(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def get_all_essences(data: Dict) -> Set[str]:
    """Get all unique essence names from both by_name and by_skill sections."""
    essences = set()
    
    # Add from by_name
    essences.update(data['by_name'].keys())
    
    # Add from by_skill
    for skill_essences in data['by_skill'].values():
        essences.update(e['essence_name'] for e in skill_essences)
    
    return essences

def verify_essences(original_file: str, optimized_file: str) -> None:
    original = load_json(original_file)
    optimized = load_json(optimized_file)
    
    # Track any discrepancies
    issues = []
    
    # 1. Check if all essences are present
    original_essences = get_all_essences(original)
    optimized_essences = {e['essence_name'] for e in optimized['essences'].values()}
    
    if missing := original_essences - optimized_essences:
        issues.append(f"Missing essences in optimized file: {missing}")
    if extra := optimized_essences - original_essences:
        issues.append(f"Extra essences in optimized file: {extra}")
        
    # 2. Check all essence properties
    for essence_name in original_essences:
        # Find essence in original data
        orig = None
        if essence_name in original['by_name']:
            orig = original['by_name'][essence_name]
        else:
            # Look in by_skill
            for skill_essences in original['by_skill'].values():
                for e in skill_essences:
                    if e['essence_name'] == essence_name:
                        orig = e
                        break
                if orig:
                    break
                    
        # Find corresponding essence in optimized file
        opt = None
        for e in optimized['essences'].values():
            if e['essence_name'] == essence_name:
                opt = e
                break
                
        if not opt:
            issues.append(f"Could not find essence {essence_name} in optimized file")
            continue
            
        # Compare properties
        for key in ['gear_slot', 'modifies_skill', 'effect']:
            if orig[key] != opt[key]:
                issues.append(f"Mismatch in {essence_name} for {key}:")
                issues.append(f"  Original: {orig[key]}")
                issues.append(f"  Optimized: {opt[key]}")
                
    # 3. Verify slot indexes
    for slot in original['by_slot']:
        orig_slot_essences = {e['essence_name'] for e in original['by_slot'][slot]}
        opt_slot_essences = {optimized['essences'][slug]['essence_name'] 
                           for slug in optimized['indexes']['by_slot'][slot]}
        
        if missing := orig_slot_essences - opt_slot_essences:
            issues.append(f"Missing essences in slot {slot}: {missing}")
        if extra := opt_slot_essences - orig_slot_essences:
            # Check if the extra essence exists in by_skill
            valid_extras = set()
            for e in extra:
                for skill_essences in original['by_skill'].values():
                    if any(se['essence_name'] == e and se['gear_slot'] == slot 
                          for se in skill_essences):
                        valid_extras.add(e)
                        break
            
            real_extras = extra - valid_extras
            if real_extras:
                issues.append(f"Extra essences in slot {slot}: {real_extras}")
            
    # 4. Verify skill indexes
    for skill in original['by_skill']:
        orig_skill_essences = {e['essence_name'] for e in original['by_skill'][skill]}
        opt_skill_essences = {optimized['essences'][slug]['essence_name'] 
                            for slug in optimized['indexes']['by_skill'][skill]}
        
        if missing := orig_skill_essences - opt_skill_essences:
            issues.append(f"Missing essences in skill {skill}: {missing}")
        if extra := opt_skill_essences - orig_skill_essences:
            issues.append(f"Extra essences in skill {skill}: {extra}")
            
    # 5. Verify metadata
    orig_meta = {k: v for k, v in original['metadata'].items() 
                if k not in ['effect_types']}  # Skip effect_types as it's new
    opt_meta = {k: v for k, v in optimized['metadata'].items() 
                if k not in ['effect_types']}
    
    if orig_meta != opt_meta:
        issues.append("Metadata mismatch:")
        issues.append(f"  Original: {orig_meta}")
        issues.append(f"  Optimized: {opt_meta}")
    
    # Print results
    if issues:
        print("❌ VERIFICATION FAILED")
        print("\nIssues found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("✅ VERIFICATION PASSED")
        print("\nAll data successfully preserved in the optimized format!")
        
        # Print some statistics
        print("\nStatistics:")
        print(f"Total essences: {len(original_essences)}")
        print(f"Total slots: {len(original['by_slot'])}")
        print(f"Total skills: {len(original['by_skill'])}")

if __name__ == "__main__":
    original = "/Users/cdukes/sourcecode/dibo-api/data/indexed/classes/barbarian/essences.json"
    optimized = "/Users/cdukes/sourcecode/dibo-api/data/indexed/classes/barbarian/essences_optimized.json"
    verify_essences(original, optimized)
