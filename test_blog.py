#!/usr/bin/env python
"""Test script for blog functionality"""
from app import create_app

app = create_app()

with app.test_client() as client:
    response = client.get('/blog')
    print(f'Blog page status: {response.status_code}')
    if response.status_code == 200:
        print('✓ Blog page works!')
    else:
        print(f'✗ Error: {response.status_code}')
        print(response.data.decode()[:1000])

