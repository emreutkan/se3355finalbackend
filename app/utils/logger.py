import logging
import os
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(app):
    """Setup comprehensive logging for the Flask application"""
    
    # Get log level from config or environment
    log_level = getattr(app.config, 'LOG_LEVEL', 
                       os.environ.get('LOG_LEVEL', 'INFO')).upper()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console Handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Configure Flask app logger
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Configure specific loggers
    loggers_to_configure = [
        'werkzeug',  # Flask development server
        'sqlalchemy.engine',  # SQL queries
        'sqlalchemy.pool',  # Connection pool
        'urllib3',  # HTTP requests
        'requests',  # HTTP requests
    ]
    
    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        # Set SQLAlchemy to WARNING to reduce noise unless in debug mode
        if logger_name.startswith('sqlalchemy') and log_level != 'DEBUG':
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.INFO)
    
    # Log initial setup
    app.logger.info("[+] Logging system initialized")
    app.logger.info(f"[i] Log level: {log_level}")

    return app.logger


def get_request_logger():
    """Get a logger for request-specific logging"""
    return logging.getLogger('imdb_api.requests')


def get_database_logger():
    """Get a logger for database operations"""
    return logging.getLogger('imdb_api.database')


def get_auth_logger():
    """Get a logger for authentication operations"""
    return logging.getLogger('imdb_api.auth')


def log_request_info(request, response_status=None, user_id=None):
    """Log detailed request information"""
    logger = get_request_logger()
    
    user_info = f" | User: {user_id}" if user_id else ""
    status_info = f" | Status: {response_status}" if response_status else ""
    
    logger.info(
        f"{request.method} {request.path} | "
        f"IP: {request.remote_addr} | "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:100]}"
        f"{user_info}{status_info}"
    )


def log_database_operation(operation, table=None, record_id=None, error=None):
    """Log database operations"""
    logger = get_database_logger()
    
    if error:
        logger.error(f"DB {operation} failed | Table: {table} | ID: {record_id} | Error: {str(error)}")
    else:
        logger.info(f"DB {operation} | Table: {table} | ID: {record_id}")


def log_auth_event(event, user_email=None, success=True, error=None):
    """Log authentication events"""
    logger = get_auth_logger()
    
    status = "SUCCESS" if success else "FAILED"
    user_info = f" | User: {user_email}" if user_email else ""
    error_info = f" | Error: {str(error)}" if error else ""
    
    if success:
        logger.info(f"AUTH {event} {status}{user_info}")
    else:
        logger.warning(f"AUTH {event} {status}{user_info}{error_info}")
