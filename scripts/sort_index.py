#!/usr/bin/env python3
import json

def sort_index_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Sort the index dictionary by keys (gem names)
    data['index'] = dict(sorted(data['index'].items()))
    
    # Update timestamp
    data['metadata']['last_updated'] = "2025-01-13T00:17:20-05:00"
    
    # Write back with consistent formatting
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    index_path = "/Users/cdukes/sourcecode/dibo-api/data/indexed/gems/index.json"
    sort_index_file(index_path)
    print("Index file sorted successfully")
