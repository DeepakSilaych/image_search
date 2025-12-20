#!/usr/bin/env python3
"""
CLI launcher for development
Usage: uv run python cli.py <command> [options]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from image_search.cli import main

if __name__ == "__main__":
    main()

