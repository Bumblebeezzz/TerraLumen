"""
Application entry point
"""

from app import create_app, db
from app.models import User, Article, MembershipTransaction

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Article': Article, 'MembershipTransaction': MembershipTransaction}

if __name__ == '__main__':
    # Use environment variable for port (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

