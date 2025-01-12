#!/usr/bin/env python3
"""Script to run API tests."""

import os
import sys
import pytest
from pathlib import Path
from rich.console import Console

console = Console()

def main() -> None:
    """Run API tests."""
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Set up test environment
    os.environ["TESTING"] = "1"
    os.environ["DATA_PATH"] = str(project_root / "data/indexed")
    
    # Get test path from command line argument or use all tests
    test_path = sys.argv[1] if len(sys.argv) > 1 else str(project_root / "tests")
    
    # Run tests
    console.print(f"\n[yellow]Running tests from: {test_path}[/yellow]")
    pytest.main([
        test_path,
        "-v",
        "--capture=no",
        "--log-cli-level=INFO"
    ])

if __name__ == "__main__":
    main()
