#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def check_gem_file(file_path):
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return f"Error reading {file_path}: {str(e)}"
        
    if 'ranks' not in data:
        return "Missing 'ranks' object"
        
    missing = []
    todo = []
    expected_ranks = set(str(i) for i in range(1, 11))  # 1 to 10
    found_ranks = set(str(i) for i in data['ranks'].keys())
    
    missing_ranks = expected_ranks - found_ranks
    if missing_ranks:
        missing.append(f"Missing ranks: {', '.join(sorted(missing_ranks))}")
    
    # Check for TODO or incomplete ranks
    for rank, info in data['ranks'].items():
        if 'effects' not in info:
            missing.append(f"Rank {rank} missing 'effects' array")
            continue
            
        for effect in info['effects']:
            if effect.get('type') == 'todo' or 'TODO' in effect.get('description', ''):
                todo.append(f"Rank {rank} has TODO")
    
    return '\n'.join(missing + todo) if (missing or todo) else None

def main():
    base_dir = "/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/core"
    star_dirs = ["1star", "2star", "5star"]
    
    missing_data = defaultdict(dict)
    
    for star_dir in star_dirs:
        dir_path = os.path.join(base_dir, star_dir)
        for file_name in os.listdir(dir_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(dir_path, file_name)
                result = check_gem_file(file_path)
                if result:
                    missing_data[star_dir][file_name] = result
    
    # Generate markdown report
    report = [
        "# Missing Gem Data Report",
        f"\nLast Updated: 2025-01-13T00:19:02-05:00\n",
        "This document tracks missing or incomplete data in gem files.",
        "## Issues by Star Rating\n"
    ]
    
    for star_dir in star_dirs:
        if star_dir in missing_data:
            report.append(f"\n### {star_dir}\n")
            for file_name, issues in sorted(missing_data[star_dir].items()):
                report.append(f"#### {file_name}")
                report.append(issues)
                report.append("")
    
    with open("/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/missing_gemdata.md", 'w') as f:
        f.write('\n'.join(report))

if __name__ == "__main__":
    main()
    print("Missing data report generated successfully")
