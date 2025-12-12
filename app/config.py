"""
Application Configuration
"""

import os
from pathlib import Path

# Get base directory - handle both development and production paths
try:
    basedir = Path(__file__).resolve().parent.parent.parent
except Exception:
    # Fallback if path resolution fails
    basedir = Path(os.getcwd())

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Render provides DATABASE_URL for PostgreSQL, otherwise use SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render uses PostgreSQL, but the URL might start with postgres://
        # SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Development: use SQLite with relative path
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/terralumen.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Email configuration (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'contact@terralumen.org'
    
    # Application settings
    POSTS_PER_PAGE = 10
    MEMBERSHIP_TYPES = ['annual', 'lifetime', 'supporter']
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

