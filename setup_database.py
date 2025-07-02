#!/usr/bin/env python3
"""
Database Setup Script for IMDB Clone API
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Setup database with tables"""
    
    # Load environment variables
    load_dotenv()
    
    print("🗃️  IMDB Clone API - Database Setup")
    print("="*50)
    
    try:
        # Import app and database utilities
        from app import create_app
        from app.utils.database import ensure_database_ready
        
        # Create Flask app
        app = create_app()
        
        # Initialize database
        print("🔄 Initializing database...")
        
        with app.app_context():
            if ensure_database_ready(app):
                print("✅ Database setup completed successfully!")
                print("\n📋 Summary:")
                print("   • Database connection verified")
                print("   • All tables created")
                print("   • Ready for use")
                
                # Show which database is being used
                db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
                if 'mysql' in db_url:
                    print("   • Using MySQL database")
                elif 'mssql' in db_url:
                    print("   • Using Azure SQL Database")
                else:
                    print(f"   • Using database: {db_url[:50]}...")
                
                print("\n🚀 You can now run the application with:")
                print("   python run.py")
                print("   python run_local_mysql.py")
                print("   python run_with_azure.py")
                
            else:
                print("❌ Database setup failed!")
                print("\n💡 Please check:")
                print("   • Database server is running")
                print("   • Database exists and credentials are correct")
                print("   • Network connectivity (for remote databases)")
                return 1
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure you have installed dependencies:")
        print("   pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        print("\n💡 Check the error message above and:")
        print("   • Verify database configuration")
        print("   • Check database server status")
        print("   • Review logs for detailed error information")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 