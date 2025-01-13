#!/usr/bin/env python3
import json
import os
from datetime import datetime

def add_metadata_to_file(file_path):
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading {file_path}")
            return False
        
    if 'metadata' in data:
        return False  # Already has metadata
        
    data = {
        "metadata": {
            "version": "1.0",
            "last_updated": "2025-01-13T00:13:37-05:00"
        },
        **data
    }
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    return True

def process_directory(directory):
    updated = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                if add_metadata_to_file(file_path):
                    print(f"Updated {file_path}")
                    updated += 1
    return updated

if __name__ == "__main__":
    base_dir = "/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/core"
    star_dirs = ["1star", "2star", "5star"]
    
    total_updated = 0
    for star_dir in star_dirs:
        dir_path = os.path.join(base_dir, star_dir)
        updated = process_directory(dir_path)
        print(f"\nUpdated {updated} files in {star_dir}")
        total_updated += updated
    
    print(f"\nTotal files updated: {total_updated}")
