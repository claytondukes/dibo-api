#!/usr/bin/env python3
import json
from collections import defaultdict

def find_duplicate_keys(file_path):
    # Read the file content as text first to preserve line numbers
    with open(file_path, 'r') as f:
        content = f.readlines()
    
    # Track keys and their line numbers
    key_lines = defaultdict(list)
    current_line = 0
    
    for line in content:
        current_line += 1
        # Look for lines with key patterns in JSON
        if ':' in line and line.strip().startswith('"'):
            key = line.split(':')[0].strip().strip('"')
            key_lines[key].append(current_line)
    
    # Find duplicates
    duplicates = {k: v for k, v in key_lines.items() if len(v) > 1}
    
    if duplicates:
        print("Found duplicate keys:")
        for key, lines in duplicates.items():
            print(f"Key '{key}' appears on lines: {', '.join(map(str, lines))}")
    else:
        print("No duplicate keys found")

if __name__ == "__main__":
    file_path = "/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/metadata/conditions.json"
    find_duplicate_keys(file_path)
