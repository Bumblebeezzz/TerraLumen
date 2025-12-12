"""
App entry point for Render auto-detection
This file exists so Render's auto-detection works with 'gunicorn app:app'

Note: There's a package 'app/' in this directory, so when Python does 'import app',
it imports the package, not this file. This file must be loaded explicitly.
"""
import os
import sys
import importlib.util

# Get the directory containing this file
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Method 1: Try to import from the app package directly
try:
    # Add parent directory to path to ensure we can import the app package
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    
    # Import create_app from the app package (the directory app/)
    from app import create_app
    
    # Create the Flask application instance
    app = create_app()
    
except Exception as e:
    # Method 2: If that fails, load run.py directly
    try:
        run_path = os.path.join(_current_dir, 'run.py')
        if os.path.exists(run_path):
            spec = importlib.util.spec_from_file_location("run_module", run_path)
            run_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(run_module)
            app = run_module.app
        else:
            raise ImportError(f"run.py not found at {run_path}")
    except Exception as e2:
        # Method 3: Last resort - create app directly
        print(f"ERROR: Failed to create app: {e}, {e2}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

# Export app for gunicorn
__all__ = ['app']
