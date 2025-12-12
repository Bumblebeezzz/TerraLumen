"""
TerraLumen Flask Application
Initialization and configuration
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

# Load environment variables (silently fail if .env doesn't exist)
try:
    load_dotenv()
except Exception:
    pass  # .env file is optional

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='development'):
    """Application factory pattern"""
    import sys
    print("Creating Flask application instance...", file=sys.stderr)
    app = Flask(__name__)
    
    # Load configuration
    try:
        print("Loading configuration...", file=sys.stderr)
        from app.config import Config
        app.config.from_object(Config)
        print("✓ Configuration loaded", file=sys.stderr)
    except Exception as e:
        print(f"✗ ERROR: Failed to load config: {e}", file=sys.stderr)
        raise
    
    # Initialize extensions with app
    print("Initializing extensions...", file=sys.stderr)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    print("✓ Extensions initialized", file=sys.stderr)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        try:
            from app.models import User
            return User.query.get(int(user_id))
        except Exception:
            # Return None if user not found or database error
            return None
    
    # Register blueprints
    print("Registering blueprints...", file=sys.stderr)
    # Main routes (required)
    try:
        from app.routes import main_bp
        app.register_blueprint(main_bp)
        print("✓ main_bp registered", file=sys.stderr)
    except Exception as e:
        print(f"✗ ERROR: Failed to register main_bp: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise
    
    # Auth routes (required)
    try:
        from app.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✓ auth_bp registered", file=sys.stderr)
    except Exception as e:
        print(f"✗ ERROR: Failed to register auth_bp: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise
    
    # Admin routes (optional - only if admin module exists)
    try:
        from app.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        print("✓ admin_bp registered", file=sys.stderr)
    except ImportError:
        # Admin module is optional
        print("⚠ admin_bp not found (optional)", file=sys.stderr)
        pass
    except Exception as e:
        print(f"⚠ WARNING: Failed to register admin_bp: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    # Stripe routes (optional - only if stripe module exists)
    try:
        from app.stripe_handler import stripe_bp
        app.register_blueprint(stripe_bp, url_prefix='/stripe')
        print("✓ stripe_bp registered", file=sys.stderr)
    except ImportError:
        # Stripe module is optional
        print("⚠ stripe_bp not found (optional)", file=sys.stderr)
        pass
    except Exception as e:
        print(f"⚠ WARNING: Failed to register stripe_bp: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors"""
        from flask import render_template
        try:
            db.session.rollback()
        except Exception:
            pass  # Ignore rollback errors if database is not available
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            # Fallback if template is missing
            return '<h1>500 Server Error</h1><p>An error occurred.</p>', 500
    
    print("✓ Flask app initialization complete!", file=sys.stderr)
    return app
