import json
import os
from pathlib import Path
""" ONE TIME USE FOR MIGRATION"""
exit

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def get_effect_conditions(effect_desc, gem_conditions):
    """Determine which conditions apply to this specific effect."""
    conditions = []
    for cond in gem_conditions:
        # If any part of the condition description appears in the effect description,
        # or if it's a general condition that applies to all effects (like on_attack)
        if (cond.get("description", "").lower() in effect_desc.lower() or
            cond.get("trigger") in ["on_attack", "on_hit"]):
            cond_type = (cond.get("trigger") or cond.get("state") or 
                        cond.get("effect_category") or cond.get("skill_type") or 
                        cond.get("target_state"))
            if cond_type and cond_type not in conditions:
                conditions.append(cond_type)
    return conditions

def simplify_gem_file(gem_data, conditions_data):
    """Convert gem file to new format with just core properties and effects."""
    gem_name = gem_data["name"]
    gem_conditions = conditions_data["conditions"].get(gem_name, [])
    
    return {
        "name": gem_name,
        "stars": gem_data.get("stars", "1"),  # Default to 1 if not specified
        "ranks": {
            str(rank): {
                "effects": [
                    {
                        "type": effect.get("type", "generic_effect"),
                        "description": effect.get("description", ""),
                        "conditions": get_effect_conditions(effect.get("description", ""), gem_conditions)
                    }
                    for effect in rank_data.get("effects", [])
                ]
            }
            for rank, rank_data in gem_data.get("ranks", {}).items()
        }
    }

def main():
    base_dir = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed/gems")
    
    # Load conditions
    conditions = load_json(base_dir / "metadata/conditions.json")
    
    # Process each star rating directory
    for star_dir in ["1star", "2star", "5star"]:
        gem_dir = base_dir / "core" / star_dir
        for gem_file in gem_dir.glob("*.json"):
            print(f"Processing {gem_file}")
            
            # Load and simplify gem data
            gem_data = load_json(gem_file)
            simplified_data = simplify_gem_file(gem_data, conditions)
            
            # Save updated gem file
            save_json(simplified_data, gem_file)

if __name__ == "__main__":
    main()
