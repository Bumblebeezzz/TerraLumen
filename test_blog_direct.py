#!/usr/bin/env python
"""Direct test of blog route"""
import sys
import traceback
from app import create_app

app = create_app()

# Enable detailed error reporting
app.config['DEBUG'] = True
app.config['TESTING'] = False

try:
    with app.app_context():
        from app.routes import main_bp
        from app.utils.blog_loader import load_blog_articles
        
        # Test loading articles
        articles = load_blog_articles()
        print(f'✓ Loaded {len(articles)} articles')
        
        # Test rendering
        from flask import render_template_string
        template = "{% for a in articles %}{{ a.title }}{% endfor %}"
        result = render_template_string(template, articles=articles)
        print(f'✓ Template rendering works')
        
        # Test full blog route
        with app.test_client() as client:
            response = client.get('/blog')
            print(f'✓ Blog route status: {response.status_code}')
            if response.status_code == 200:
                html = response.data.decode('utf-8', errors='ignore')
                if 'Welcome to TerraLumen' in html or 'Tesla Plasma' in html:
                    print('✓ Blog page works correctly!')
                else:
                    print('⚠ Blog loads but content may be missing')
            else:
                print(f'✗ Error {response.status_code}')
                print(response.data.decode('utf-8', errors='ignore')[:1500])
except Exception as e:
    print(f'✗ Exception: {e}')
    traceback.print_exc()

