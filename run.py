#!/usr/bin/env python3
"""
Unified run script for IMDB Clone API.
Supports both local MySQL and Azure SQL Database environments.
"""
import os
from dotenv import load_dotenv
from app import create_app

# --- Configuration Selection ---
# Comment out the line below to use Azure SQL Database
USE_LOCAL_MYSQL = False
# -----------------------------

def load_config():
    """Load configuration for Azure SQL Database environment"""
    load_dotenv()  # Load base .env file

    # --- Azure SQL Database Configuration ---
    print("[+] Using Azure SQL Database configuration")
    # These can be set in your .env file or directly as environment variables
    os.environ.setdefault('DB_SERVER_NAME', 'webdevfinaldbs3355.database.windows.net')
    os.environ.setdefault('DB_ADMIN_LOGIN', 'your_admin')
    os.environ.setdefault('DB_PASSWORD', 'your_password')
    os.environ.setdefault('DB_DATABASE_NAME', 'imdbapp')

    # Unset MySQL-specific variables to avoid conflicts
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']

# Load Azure configuration
load_config()

# Create the Flask app instance - this is what Gunicorn will use
app = create_app()

if __name__ == '__main__':
    print("[+] Starting IMDB Clone API...")

    # Get Flask run parameters
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = 8000

    # Display startup information
    print("="*50)
    server_name = os.environ.get('DB_SERVER_NAME', 'Not Set')
    print(f"🗃️  Database: Azure SQL Database ({server_name})")

    print(f"🚀 Starting server on {host}:{port}")
    print(f"🐛 Debug mode: {debug}")
    print("="*50)

    # Run the Flask app
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )