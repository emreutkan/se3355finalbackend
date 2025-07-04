from flask import Flask, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
import os
from datetime import datetime

from .config import Config
from .utils.logger import setup_logging, log_request_info
from .utils.database import ensure_database_ready

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging first
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Use production API directly with HTTPS only
    api_host = "be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net"
    api_environment = "production"
    
    # Initialize Swagger for API documentation
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'swagger',
                "route": '/swagger.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "IMDB Clone API",
            "description": f"A comprehensive movie database API with authentication, search, ratings, and more. Currently running in {api_environment} environment.",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@imdbclone.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "host": api_host,
        "basePath": "/api",
        "schemes": ["https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "Movies",
                "description": "Movie operations and ratings"
            },
            {
                "name": "Actors",
                "description": "Actor information"
            },
            {
                "name": "Search",
                "description": "Search functionality"
            },
            {
                "name": "Users",
                "description": "User profile and watchlist management"
            },
            {
                "name": "System",
                "description": "System health and status endpoints"
            },
            {
                "name": "Development",
                "description": "Development-specific endpoints"
            }
        ]
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    # Add request logging middleware
    @app.before_request
    def log_request():
        """Log all incoming requests"""
        from flask_jwt_extended import get_jwt_identity
        try:
            user_id = get_jwt_identity()
        except:
            user_id = None
        
        # Skip logging for static files and health checks
        if not request.path.startswith('/static') and request.path != '/api/health':
            log_request_info(request, user_id=user_id)

    @app.after_request
    def log_response(response):
        """Log response status"""
        if not request.path.startswith('/static') and request.path != '/api/health':
            app.logger.debug(f"Response: {response.status_code} for {request.method} {request.path}")
        return response

    # Initialize database and create tables if needed
    if not ensure_database_ready(app):
        app.logger.error("❌ Failed to initialize database. Application may not work correctly.")
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.movies import movies_bp
    from .routes.actors import actors_bp
    from .routes.search import search_bp
    from .routes.users import users_bp
    from .routes.dev import dev_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(actors_bp, url_prefix='/api/actors')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(dev_bp, url_prefix='/api/dev')

    # Root redirect to Swagger documentation
    @app.route('/')
    def root():
        """Redirect to API documentation"""
        return redirect('/swagger/')
    
    # API base redirect to Swagger documentation
    @app.route('/api')
    @app.route('/api/')
    def api_root():
        """Redirect API base URL to Swagger documentation"""
        return redirect('/swagger/')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint
        ---
        tags:
          - System
        summary: Health check
        description: Check if the API is running and healthy
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                message:
                  type: string
                  example: "IMDB Clone API is running"
                environment:
                  type: string
                  example: "production"
                host:
                  type: string
                  example: "be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net"
        """
        return jsonify({
            'status': 'healthy',
            'message': 'IMDB Clone API is running',
            'environment': api_environment,
            'host': api_host
        }), 200
    
    # Environment info endpoint
    @app.route('/api/info')
    def api_info():
        """
        API environment information
        ---
        tags:
          - System
        summary: API environment info
        description: Get information about the current API environment and configuration
        responses:
          200:
            description: Environment information
            schema:
              type: object
              properties:
                environment:
                  type: string
                  example: "production"
                api_host:
                  type: string
                  example: "be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net"
                schemes:
                  type: array
                  items:
                    type: string
                  example: ["https"]
                swagger_url:
                  type: string
                  example: "https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net/swagger/"
                base_path:
                  type: string
                  example: "/api"
        """
        return jsonify({
            'environment': api_environment,
            'api_host': api_host,
            'schemes': ["https"],
            'swagger_url': f"https://{api_host}/swagger/",
            'base_path': '/api'
        }), 200

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"❌ Bad Request: {str(error)}")
        return jsonify({'msg': 'Bad request', 'details': str(error) if app.debug else None}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f"🔐 Unauthorized access attempt: {str(error)}")
        return jsonify({'msg': 'Unauthorized', 'details': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f"🚫 Forbidden access attempt: {str(error)}")
        return jsonify({'msg': 'Forbidden', 'details': 'Insufficient permissions'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.debug(f"🔍 Resource not found: {request.path}")
        return jsonify({'msg': 'Resource not found', 'path': request.path}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"💥 CRITICAL ERROR: {str(error)}", exc_info=True)
        app.logger.error(f"💥 Request details: {request.method} {request.path}")
        app.logger.error(f"💥 User: {getattr(request, 'user_id', 'Unknown')}")
        
        # In production, give more helpful error message
        if app.config.get('API_ENVIRONMENT') == 'production':
            return jsonify({
                'msg': 'Internal server error', 
                'details': 'The server encountered an error processing your request. Please try again or contact support.',
                'error_id': str(error)[:100] if hasattr(error, '__str__') else 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        else:
            return jsonify({
                'msg': 'Internal server error',
                'details': str(error),
                'type': type(error).__name__
            }), 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'msg': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'msg': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'msg': 'Authentication token required'}), 401

    return app
