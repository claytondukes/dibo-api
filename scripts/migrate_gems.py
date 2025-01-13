#!/usr/bin/env python3
"""ONE TIME USE for migration
Migrate gems to new directory structure."""
exit

import json
import os
from typing import Dict, List

# Paths
BASE_DIR = "data/indexed/gems"
OLD_GEMS_FILE = f"{BASE_DIR}/gems.json"
OLD_SYNERGIES_FILE = f"{BASE_DIR}/synergies.json"
OLD_SKILLMAP_FILE = f"{BASE_DIR}/gem_skillmap.json"
OLD_STAT_BOOSTS_FILE = f"{BASE_DIR}/stat_boosts.json"

def snake_case(name: str) -> str:
    """Convert a gem name to snake case for filename."""
    return name.lower().replace("'", "").replace(" ", "_").replace("-", "_")

def infer_categories(gem_data: Dict, stat_boosts: Dict) -> List[str]:
    """Infer gem categories based on effects and stats."""
    categories = set()
    
    # Check effects
    for rank_data in gem_data.get("ranks", {}).values():
        for effect in rank_data.get("effects", []):
            desc = effect.get("description", "").lower()
            
            # Damage categories
            if "damage" in desc:
                categories.add("damage")
                if "take" in desc:
                    categories.add("glass_cannon")
            
            # Critical hit
            if "critical" in desc:
                categories.add("critical_hit")
            
            # Movement
            if "movement" in desc or "speed" in desc:
                categories.add("mobility")
            
            # Life/survival
            if "life" in desc or "health" in desc:
                categories.add("survival")
                
            # Crowd control
            if any(term in desc for term in ["stun", "freeze", "slow", "chill"]):
                categories.add("crowd_control")
                
    return sorted(list(categories))

def infer_synergies(gem_name: str, gem_data: Dict, all_gems: Dict, skillmap: Dict) -> Dict:
    """Infer gem synergies based on effects and existing data."""
    synergies = {
        "skills": [],
        "gems": [],
        "sets": []
    }
    
    # Get skill types from skillmap
    if gem_name in skillmap:
        synergies["skills"] = skillmap[gem_name].get("skill_types", [])
    
    # Find complementary gems
    for other_name, other_data in all_gems.items():
        if other_name == gem_name:
            continue
            
        # Simple matching based on categories
        gem_cats = infer_categories(gem_data, {})
        other_cats = infer_categories(other_data, {})
        
        if set(gem_cats) & set(other_cats):
            synergies["gems"].append(other_name)
    
    return synergies

def migrate_gems():
    """Migrate gems to new structure."""
    # Load old data
    with open(OLD_GEMS_FILE) as f:
        gems = json.load(f)
    
    try:
        with open(OLD_SKILLMAP_FILE) as f:
            skillmap = json.load(f)
    except FileNotFoundError:
        skillmap = {}
    
    # Create directories
    os.makedirs(f"{BASE_DIR}/core/1star", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/core/2star", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/core/5star", exist_ok=True)
    
    # Create index
    index = {}
    
    # Migrate each gem
    for name, data in gems.items():
        if "stars" not in data:
            print(f"Skipping {name} - no stars rating")
            continue
            
        # Create new gem data with categories and synergies
        new_data = {
            "name": name,
            **{k: v for k, v in data.items() if k != "max_rank"},
            "categories": infer_categories(data, {}),
            "synergies": infer_synergies(name, data, gems, skillmap)
        }
        
        # Save to appropriate directory
        filename = f"{snake_case(name)}.json"
        filepath = f"{BASE_DIR}/core/{data['stars']}star/{filename}"
        
        with open(filepath, "w") as f:
            json.dump(new_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            
        # Update index
        index[name] = f"core/{data['stars']}star/{filename}"
        
    # Save index
    with open(f"{BASE_DIR}/index.json", "w") as f:
        json.dump(index, f, indent=2, sort_keys=True, ensure_ascii=False)
        
    print("Migration complete!")
    print(f"Migrated {len(index)} gems")
    
if __name__ == "__main__":
    migrate_gems()
