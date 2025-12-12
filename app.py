"""
App entry point for Render auto-detection
This file exists so Render's auto-detection works with 'gunicorn app:app'
"""
import os
import sys

# Import directly from the app package to create the Flask app
try:
    # Import the create_app function from the app package
    from app import create_app
    
    # Create the Flask application instance
    app = create_app()
    
except Exception as e:
    # If direct import fails, try importing from run.py
    import importlib.util
    
    run_path = os.path.join(os.path.dirname(__file__), 'run.py')
    spec = importlib.util.spec_from_file_location("run_module", run_path)
    run_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_module)
    app = run_module.app

# Export app for gunicorn
__all__ = ['app']
