"""
Vercel Serverless Entry Point for Intelligent Resume Parser
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Import the FastAPI application
from app.main import app
