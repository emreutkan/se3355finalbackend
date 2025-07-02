import os
import logging
from flask_migrate import init, migrate, upgrade
from flask import current_app

logger = logging.getLogger(__name__)

def init_database(app):
    """Initialize database with automatic migration handling"""
    
    with app.app_context():
        try:
            # Check if migrations directory exists
            # Corrected path to be at the project root
            migrations_dir = os.path.join(app.root_path, '..', 'migrations')

            if not os.path.exists(migrations_dir):
                logger.info("[+] Initializing Flask-Migrate...")
                init()
                logger.info("[+] Migrations directory created")

            # Check if database tables exist by checking if alembic version table exists
            try:
                from .. import db
                # Check if alembic version table exists - this indicates migrations have been run
                result = db.session.execute(db.text("SELECT COUNT(*) FROM alembic_version"))
                if result.scalar() > 0:
                    logger.info("[+] Database tables already exist")
                    return True
                
            except Exception:
                logger.info("[-] Database tables don't exist, creating them...")

                # Create initial migration if no migration files exist
                versions_dir = os.path.join(migrations_dir, 'versions')
                if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
                    logger.info("[+] Creating initial migration...")
                    migrate(message='Initial migration')
                    logger.info("[+] Initial migration created")

                # Run migrations to create tables
                logger.info("[+] Running database migrations...")
                upgrade()
                logger.info("[+] Database tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"[!] Database initialization failed: {str(e)}")
            return False

def create_tables_if_not_exist(app):
    """Fallback method to create tables using SQLAlchemy if migrations fail"""
    
    with app.app_context():
        try:
            from .. import db
            # Import all models to ensure they're registered
            from ..models import User, Movie, Actor, MovieActor, Rating, Watchlist, PopularitySnapshot
            
            logger.info("[+] Creating tables using SQLAlchemy...")
            db.create_all()
            logger.info("[+] Tables created successfully using SQLAlchemy")
            return True
        except Exception as e:
            logger.error(f"[!] Failed to create tables: {str(e)}")
            return False

def ensure_database_ready(app):
    """Ensure database is ready with tables created"""
    
    logger.info("[i] Checking database setup...")

    # First try with migrations
    if init_database(app):
        return True
    
    # Fallback to direct table creation
    logger.warning("[!] Migrations failed, trying direct table creation...")
    if create_tables_if_not_exist(app):
        return True
    
    # If both fail, provide helpful error message
    logger.error("[!] Could not initialize database. Please check:")
    logger.error("   • Database server is running")
    logger.error("   • Database exists and is accessible")
    logger.error("   • Connection credentials are correct")
    return False
