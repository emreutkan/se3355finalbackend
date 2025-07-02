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

def load_config(use_local_mysql):
    """Load configuration based on the selected environment"""
    load_dotenv()  # Load base .env file

    if use_local_mysql:
        # --- MySQL (Local Development) ---
        print("[+] Using local MySQL configuration")
        os.environ['DATABASE_URL'] = 'mysql+pymysql://root:123456789@127.0.0.1:3306/webdev1'
        os.environ['REDIS_URL'] = 'memory://'
        # Unset Azure-specific variables to avoid conflicts
        for key in ['DB_SERVER_NAME', 'DB_ADMIN_LOGIN', 'DB_PASSWORD', 'DB_DATABASE_NAME']:
            if key in os.environ:
                del os.environ[key]
    else:
        # --- Azure SQL Database ---
        print("[+] Using Azure SQL Database configuration")
        # These can be set in your .env file or directly as environment variables
        # Example values are provided for clarity
        os.environ.setdefault('DB_SERVER_NAME', 'your_server.database.windows.net')
        os.environ.setdefault('DB_ADMIN_LOGIN', 'your_admin')
        os.environ.setdefault('DB_PASSWORD', 'your_password')
        os.environ.setdefault('DB_DATABASE_NAME', 'imdbapp')
        os.environ['REDIS_URL'] = 'memory://'

if __name__ == '__main__':
    print("[+] Starting IMDB Clone API...")

    # Load the appropriate configuration BEFORE creating the app
    load_config(USE_LOCAL_MYSQL)

    # Create the Flask app
    app = create_app()

    # Get Flask run parameters
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))

    # Display startup information
    print("="*70)
    if USE_LOCAL_MYSQL:
        print(f"[i] Database: MySQL (127.0.0.1:3306/webdev1)")
    else:
        server_name = os.environ.get('DB_SERVER_NAME', 'Not Set')
        print(f"[i] Database: Azure SQL Database ({server_name})")

    print(f"[i] Starting server on {host}:{port}")
    print(f"[i] Debug mode: {debug}")
    print(f"[i] Swagger documentation: http://{host}:{port}/swagger/")
    print(f"[i] Health check: http://{host}:{port}/api/health")
    print("="*70)
    
    print("[i] Initializing database connection...")

    try:
        with app.app_context():
            from app import db
            # Test database connection
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("[+] Database connection successful")

        print(f"[+] Starting Flask server on {host}:{port}")
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except Exception as e:
        print(f"[!] Error starting application: {e}")
        print("[?] Troubleshooting tips:")
        if USE_LOCAL_MYSQL:
            print("   - Is your MySQL server running on localhost:3306?")
            print("   - Did you create the 'webdev1' database?")
            print("   - Are your MySQL credentials (root:123456789) correct?")
            print("   - Have you installed the necessary driver: pip install PyMySQL")
        else:
            print("   - Are your Azure SQL Database credentials set correctly in your .env file?")
            print("   - Have you installed the necessary driver: pip install pyodbc")
            print("   - Is the ODBC Driver 17 for SQL Server installed?")
            print("   - Do your firewall settings allow connection to Azure?")
        print("   - Have you installed all dependencies: pip install -r requirements.txt")
        print("   - Check the 'logs' directory for more detailed error information.")
