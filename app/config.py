import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')
    
    # Database configuration
    # Check if Azure SQL Database credentials are provided
    db_server = os.environ.get('DB_SERVER_NAME')
    db_login = os.environ.get('DB_ADMIN_LOGIN')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_DATABASE_NAME', 'webdevfinaldb')
    
    if db_server and db_login and db_password:
        # Azure SQL Database connection (production)
        SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{db_login}:{db_password}@{db_server}:1433/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"
        print(f"🗃️  Database: Azure SQL Database ({db_server})")
    else:
        # Default to environment variable or MySQL for local development
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL', 
            'mysql+pymysql://root:123456789@127.0.0.1:3306/webdev1'
        )
        print(f"🗃️  Database: Local MySQL (127.0.0.1:3306)")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_REFRESH_TOKEN_EXPIRES = False
    JWT_ALGORITHM = 'HS256'
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # API Environment configuration
    API_ENVIRONMENT = os.environ.get('API_ENVIRONMENT', 'local')


    BACKEND_URL = os.environ.get('PRODUCTION_BACKEND_URL', 'https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net')
    FRONTEND_URL = os.environ.get('PRODUCTION_FRONTEND_URL', 'https://proud-ground-0a0435f03.2.azurestaticapps.net')


    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = f"{BACKEND_URL}/api/auth/google/callback"
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_TO_FILE = os.environ.get('LOG_TO_FILE', 'true').lower() == 'true'
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # API Environment configuration
    PRODUCTION_API_HOST = os.environ.get('PRODUCTION_API_HOST', 'https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
