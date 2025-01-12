#!/usr/bin/env python3
"""Script to run API tests."""

import os
import sys
import logging
import pytest
from pathlib import Path
from datetime import datetime
from typing import List

from api.core.config import get_settings

logger = logging.getLogger(__name__)

def setup_logging() -> Path:
    """Set up logging configuration.
    
    Returns:
        Path to the log file
    """
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Set up log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_run_{timestamp}.log"
    
    # Configure root logger to use settings.log_level for file
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file)
        ]
    )
    
    return log_file

def parse_pytest_args(argv: List[str], project_root: Path) -> List[str]:
    """Parse command line arguments for pytest.
    
    Args:
        argv: Command line arguments
        project_root: Project root directory
        
    Returns:
        List of pytest arguments
    """
    # Get test path from command line argument or use all tests
    test_path = argv[1] if len(argv) > 1 else str(project_root / "tests")
    
    # Start with test path
    pytest_args = [test_path]
    
    # Default arguments if not overridden by command line
    defaults = {
        "--capture": "tee-sys",  # Capture output but still show it
        "--tb": "short",  # Shorter traceback format
        "-v": None  # Verbose output
    }
    
    # Add any arguments from command line, skipping the script name
    cmd_args = argv[2:] if len(argv) > 2 else []
    
    # Parse command line arguments to find overrides
    overridden = set()
    i = 0
    while i < len(cmd_args):
        arg = cmd_args[i]
        # Handle both --arg=value and --arg value formats
        if "=" in arg:
            key = arg.split("=")[0]
            overridden.add(key)
            pytest_args.append(arg)
        else:
            key = arg
            overridden.add(key)
            pytest_args.append(arg)
            # If there's a value after the flag, add it too
            if i + 1 < len(cmd_args) and not cmd_args[i + 1].startswith("-"):
                pytest_args.append(cmd_args[i + 1])
                i += 1
        i += 1
    
    # Add default arguments that weren't overridden
    for arg, value in defaults.items():
        if arg not in overridden:
            pytest_args.append(arg)
            if value is not None:
                if "=" in arg:
                    pytest_args[-1] = f"{arg}={value}"
                else:
                    pytest_args.append(value)
    
    return pytest_args

def main() -> None:
    """Run API tests."""
    # Set up logging
    log_file = setup_logging()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Set up test environment
    os.environ["TESTING"] = "1"
    os.environ["DATA_PATH"] = str(project_root / "data/indexed")
    
    # Parse pytest arguments
    pytest_args = parse_pytest_args(sys.argv, project_root)
    
    # Run tests and get exit code
    logger.debug(f"Running pytest with args: {' '.join(pytest_args)}")
    exit_code = pytest.main(pytest_args)
    
    # Log completion status
    if exit_code == 0:
        logger.info("All tests passed successfully")
    else:
        logger.error(f"Tests failed with exit code: {exit_code}")
    
    logger.debug(f"Full test output available in: {log_file}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
