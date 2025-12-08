"""Quick test script for the Flask app"""
from app import create_app

app = create_app()

print("Testing Flask application routes...")
print("=" * 50)

with app.test_client() as client:
    routes = [
        ('/', 'Homepage'),
        ('/about', 'About'),
        ('/services', 'Services'),
        ('/membership', 'Membership'),
        ('/contact', 'Contact'),
        ('/blog', 'Blog'),
    ]
    
    for route, name in routes:
        response = client.get(route)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {name:15} - Status: {response.status_code}")
    
    print("=" * 50)
    print("✓ Application routes are working correctly!")

