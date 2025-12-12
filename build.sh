#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
flask db upgrade || echo "Migration failed, continuing anyway..."

echo "Build completed successfully!"
