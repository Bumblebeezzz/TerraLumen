"""
App entry point for Render auto-detection
This file exists so Render's auto-detection works with 'gunicorn app:app'
"""
import os
import sys

# Force import from run.py by using importlib
import importlib.util

# Get the path to run.py
run_path = os.path.join(os.path.dirname(__file__), 'run.py')

# Load run.py as a module
spec = importlib.util.spec_from_file_location("run_module", run_path)
run_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_module)

# Get the app from run_module
app = run_module.app

# Export app for gunicorn
__all__ = ['app']
