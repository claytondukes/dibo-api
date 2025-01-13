#!/usr/bin/env python3
import json
import os
import re
from collections import defaultdict

def extract_values(description):
    """Extract X and Y values from effect description"""
    if not description:
        return None, None
        
    # Look for patterns like "X% base damage + Y"
    damage_match = re.search(r'(\d+)%.*?(\d+)', description)
    if damage_match:
        return damage_match.group(1), damage_match.group(2)
    return None, None

def format_gem_section(name, data):
    """Format a single gem's section with markdown table"""
    template = get_gem_description(data)
    if not template:
        return ""
        
    # Replace actual numbers with X and Y in template
    x, y = extract_values(template)
    if x and y:
        template = template.replace(f"{x}%", "X%")
        template = template.replace(f" {y}", " Y")
    
    lines = [
        f"### {name}\n",
        f"{template}\n",
        "| Rank | X   | Y   |",
        "|------|-----|-----|"
    ]
    
    for rank in range(1, 11):
        rank_str = str(rank)
        if rank_str in data.get('ranks', {}):
            effects = data['ranks'][rank_str].get('effects', [])
            if effects and not any(e.get('type') == 'todo' or 'TODO' in e.get('description', '') for e in effects):
                x, y = extract_values(effects[0].get('description', ''))
                if x and y:
                    lines.append(f"| {rank:<4} | {x:<3} | {y:<3} |")
                    continue
        lines.append(f"| {rank:<4} | ?   | ?   |")
    
    return "\n".join(lines) + "\n\n"

def get_gem_description(data):
    """Extract the template description from rank 1"""
    if 'ranks' not in data or '1' not in data['ranks']:
        return None
    
    effects = data['ranks']['1'].get('effects', [])
    if not effects:
        return None
    
    return effects[0].get('description', None)

def main():
    base_dir = "/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/core"
    star_dirs = {
        "5star": "5★",
        "2star": "2★",
        "1star": "1★"
    }
    
    report = [
        "# Missing Gem Data Report\n",
        f"Last Updated: 2025-01-13T00:22:06-05:00\n",
        "This document tracks missing or incomplete data in gem files.\n"
    ]
    
    for star_dir, star_symbol in star_dirs.items():
        gems_with_missing = []
        dir_path = os.path.join(base_dir, star_dir)
        
        # First pass: collect gems with missing data
        for file_name in sorted(os.listdir(dir_path)):
            if not file_name.endswith('.json'):
                continue
                
            file_path = os.path.join(dir_path, file_name)
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue
                    
            # Check if gem has missing data
            has_missing = False
            for rank in range(1, 11):
                rank_str = str(rank)
                if rank_str not in data.get('ranks', {}):
                    has_missing = True
                    break
                effects = data['ranks'][rank_str].get('effects', [])
                if any(e.get('type') == 'todo' or 'TODO' in e.get('description', '') for e in effects):
                    has_missing = True
                    break
            
            if has_missing:
                gems_with_missing.append((data.get('name', file_name.replace('.json', '')), data))
        
        # If there are gems with missing data, add the section
        if gems_with_missing:
            report.append(f"## {star_symbol} Gems\n")
            for name, data in gems_with_missing:
                report.append(format_gem_section(name, data))
    
    with open("/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/missing_gemdata.md", 'w') as f:
        f.write('\n'.join(report))

if __name__ == "__main__":
    main()
    print("Missing data report generated successfully")
