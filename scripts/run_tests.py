#!/usr/bin/env python3
"""Script to run API tests."""

import os
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
    
    # Run tests
    console.print("\n[yellow]Running API tests...[/yellow]")
    pytest.main([
        str(project_root / "tests"),
        "-v",
        "--capture=no",
        "--log-cli-level=INFO"
    ])

if __name__ == "__main__":
    main()
