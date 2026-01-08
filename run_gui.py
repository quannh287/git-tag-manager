#!/usr/bin/env python3
"""
Entry point script for PyInstaller build.
This avoids relative import issues.
"""
import sys
import os

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_tag_manager.gui import main

if __name__ == "__main__":
    main()
