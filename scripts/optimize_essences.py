import json
import os
from typing import Dict, List, Any

def optimize_essences(input_file: str, output_file: str) -> None:
    """Convert the essence file to an optimized format."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Initialize new structure
    optimized = {
        "metadata": data["metadata"],
        "essences": {},
        "indexes": {
            "by_slot": {
                "Helm": [], "Chest": [], "Legs": [],
                "Main Hand": [], "Off-Hand": [], "Shoulder": []
            },
            "by_skill": {}
        }
    }
    
    # Initialize by_skill index with all skills from the original data
    for skill in data["by_skill"].keys():
        optimized["indexes"]["by_skill"][skill] = []
    
    # First pass: process by_name essences
    for essence_name, essence in data["by_name"].items():
        # Create slug from essence name
        slug = essence_name.lower().replace("'", "").replace(" ", "_")
        
        # Add to main essences dict
        optimized["essences"][slug] = {
            "essence_name": essence_name,
            "gear_slot": essence["gear_slot"],
            "modifies_skill": essence["modifies_skill"],
            "effect": essence["effect"],
            "effect_type": essence.get("effect_type", "damage"),
            "effect_tags": essence.get("effect_tags", ["damage"])
        }
        
        # Add to indexes
        optimized["indexes"]["by_slot"][essence["gear_slot"]].append(slug)
        optimized["indexes"]["by_skill"][essence["modifies_skill"]].append(slug)
    
    # Second pass: check for essences that only appear in by_skill
    for skill, essences in data["by_skill"].items():
        for essence in essences:
            essence_name = essence["essence_name"]
            slug = essence_name.lower().replace("'", "").replace(" ", "_")
            
            # If we haven't processed this essence yet
            if slug not in optimized["essences"]:
                # Add to main essences dict
                optimized["essences"][slug] = {
                    "essence_name": essence_name,
                    "gear_slot": essence["gear_slot"],
                    "modifies_skill": essence["modifies_skill"],
                    "effect": essence["effect"],
                    "effect_type": "damage",  # default
                    "effect_tags": ["damage"]  # default
                }
                
                # Add to indexes
                optimized["indexes"]["by_slot"][essence["gear_slot"]].append(slug)
                optimized["indexes"]["by_skill"][essence["modifies_skill"]].append(slug)
    
    # Sort all lists for consistency
    for slot_list in optimized["indexes"]["by_slot"].values():
        slot_list.sort()
    for skill_list in optimized["indexes"]["by_skill"].values():
        skill_list.sort()
    
    # Write optimized file
    with open(output_file, 'w') as f:
        json.dump(optimized, f, indent=2)

if __name__ == "__main__":
    base_dir = "/Users/cdukes/sourcecode/dibo-api"
    input_file = os.path.join(base_dir, "data/indexed/classes/barbarian/essences.json")
    output_file = os.path.join(base_dir, "data/indexed/classes/barbarian/essences_optimized.json")
    optimize_essences(input_file, output_file)
