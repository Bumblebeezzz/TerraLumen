"""
Application entry point
"""

import os
from app import create_app, db

app = create_app()

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

