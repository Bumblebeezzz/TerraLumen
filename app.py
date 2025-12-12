"""
App entry point that loads wsgi.py to avoid package conflict
This file is loaded when Render runs 'gunicorn app:app'
"""
import os
import sys
import importlib.util

# Load wsgi.py directly to avoid package conflict
_current_dir = os.path.dirname(os.path.abspath(__file__))
wsgi_path = os.path.join(_current_dir, 'wsgi.py')

if os.path.exists(wsgi_path):
    spec = importlib.util.spec_from_file_location("wsgi", wsgi_path)
    wsgi_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wsgi_module)
    app = wsgi_module.app
else:
    # Fallback: create app directly
    from app import create_app
    app = create_app()

__all__ = ['app']
