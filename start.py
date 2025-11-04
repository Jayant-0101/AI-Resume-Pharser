#!/usr/bin/env python3
"""
Main startup script for Resume Parser
Simple redirect to the recommended startup script
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to project root
os.chdir(project_root)

# Run simple_start directly
if __name__ == "__main__":
    # Import and execute the startup script
    import subprocess
    script_path = project_root / "scripts" / "startup" / "simple_start.py"
    subprocess.run([sys.executable, str(script_path)])

