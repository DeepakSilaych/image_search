#!/usr/bin/env python3
"""
Quick launcher for development
Usage: uv run python run.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from image_search.app import main

if __name__ == "__main__":
    main()

