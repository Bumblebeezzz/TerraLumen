#!/usr/bin/env python
"""Test blog route and capture errors"""
import sys
from app import create_app

app = create_app()

# Enable debug mode to see errors
app.config['DEBUG'] = True

with app.test_request_context():
    try:
        from app.routes import main_bp
        from flask import url_for
        
        # Test the blog route directly
        with app.test_client() as client:
            response = client.get('/blog')
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                html = response.data.decode('utf-8', errors='ignore')
                if 'Welcome to TerraLumen' in html or 'Tesla Plasma' in html:
                    print('✓ Blog works!')
                else:
                    print('⚠ Blog loads but content missing')
                    print(html[:500])
            else:
                print('✗ Error occurred')
                print(response.data.decode('utf-8', errors='ignore')[:2000])
    except Exception as e:
        print(f'Exception: {e}')
        import traceback
        traceback.print_exc()

