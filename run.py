"""
Application entry point
"""

import os
import sys

# Log startup
print("=" * 50, file=sys.stderr)
print("Starting TerraLumen application...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)
print("=" * 50, file=sys.stderr)

try:
    print("Importing app module...", file=sys.stderr)
    from app import create_app, db
    print("Creating Flask app...", file=sys.stderr)
    app = create_app()
    print("✓ Flask app created successfully!", file=sys.stderr)
except Exception as e:
    print(f"✗ Error creating app: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

@app.shell_context_processor
def make_shell_context():
    """Shell context for Flask CLI"""
    try:
        from app.models import User, Article, MembershipTransaction
        return {'db': db, 'User': User, 'Article': Article, 'MembershipTransaction': MembershipTransaction}
    except Exception:
        # Return minimal context if models can't be imported
        return {'db': db}

if __name__ == '__main__':
    # Use environment variable for port (Render sets PORT)
    port = int(os.environ.get('PORT', 5005))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

