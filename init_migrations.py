#!/usr/bin/env python3
"""
Initialize Flask-Migrate for the IMDB Clone backend
"""

import os
from app import create_app
from flask_migrate import Migrate, init

def initialize_migrations():
    """Initialize the migrations directory"""
    app = create_app()
    
    with app.app_context():
        # Initialize migrations if not already done
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Initializing Flask-Migrate...")
            init()
            print("Migrations directory created successfully!")
        else:
            print("Migrations directory already exists.")

if __name__ == '__main__':
    initialize_migrations() 