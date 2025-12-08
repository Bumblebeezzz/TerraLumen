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
    app.run(debug=True, port=5000)

