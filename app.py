"""
App entry point for Render auto-detection
This file exists so Render's auto-detection works with 'gunicorn app:app'
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and create app from run.py
from run import app

# Export app for gunicorn
__all__ = ['app']
