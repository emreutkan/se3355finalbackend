from flask import Blueprint, jsonify, current_app
from app import db
from scripts.seed_data import seed_database
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from datetime import datetime

from ..models import User, Movie, Rating
from ..utils.logger import get_movies_logger
from ..utils.validators import validate_rating

dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/reset-database', methods=['POST'])
def reset_database():
    """
    Clear all database tables and re-seed with sample data.
    This is a protected endpoint for development purposes.
    ---
    tags:
      - Development
    summary: Reset and seed the database
    description: Clears all data from the database and populates it with initial seed data. For development use only.
    responses:
      200:
        description: Database reset and seeded successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Database has been successfully reset and seeded.
      403:
        description: Forbidden
        schema:
          type: object
          properties:
            error:
              type: string
              example: This endpoint is only available in development environment
      500:
        description: Internal Server Error
        schema:
          type: object
          properties:
            error:
              type: string
              example: An error occurred during database reset.
    """
    try:
        current_app.logger.info("[-] Starting database reset...")

        # Clear all data from tables
        # Using a more robust method to delete data without dropping tables
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            current_app.logger.info(f"Clearing table: {table.name}")
            db.session.execute(table.delete())
        db.session.commit()

        current_app.logger.info("[+] All tables cleared.")

        # Seed the database
        current_app.logger.info("[-] Seeding database with sample data...")
        seed_database()
        current_app.logger.info("[+] Database seeded successfully.")

        return jsonify(message="Database has been successfully reset and seeded."), 200

    except Exception as e:
        current_app.logger.error(f"[!] Database reset failed: {str(e)}")
        db.session.rollback()
        return jsonify(error=f"An error occurred during database reset: {str(e)}"), 500

@dev_bp.route('/debug/rating/<movie_id>', methods=['GET'])
@jwt_required()
def debug_rating_endpoint(movie_id):
    """Debug endpoint to test rating functionality
    ---
    tags:
      - Development
    summary: Debug rating endpoint
    description: Debug endpoint to check if a user can rate a specific movie
    security:
      - Bearer: []
    parameters:
      - name: movie_id
        in: path
        type: string
        required: true
        description: Movie ID to test rating for
    responses:
      200:
        description: Debug information
        schema:
          type: object
          properties:
            debug_info:
              type: object
            can_rate:
              type: boolean
            issues:
              type: array
              items:
                type: string
      500:
        description: Internal Server Error
    """
    logger = get_movies_logger()
    
    try:
        debug_info = {}
        issues = []
        can_rate = True
        
        # Check JWT and user
        current_user_id = get_jwt_identity()
        debug_info['jwt_user_id'] = current_user_id
        
        if not current_user_id:
            issues.append("No user ID found in JWT token")
            can_rate = False
        else:
            user = User.query.get(current_user_id)
            if not user:
                issues.append(f"User {current_user_id} not found in database")
                can_rate = False
            else:
                debug_info['user'] = {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.full_name,
                    'country': user.country,
                    'auth_provider': user.auth_provider
                }
        
        # Check movie
        movie = Movie.query.get(movie_id)
        if not movie:
            issues.append(f"Movie {movie_id} not found in database")
            can_rate = False
        else:
            debug_info['movie'] = {
                'id': str(movie.id),
                'title': movie.title,
                'year': movie.year
            }
            
            # Check existing rating
            if current_user_id:
                existing_rating = Rating.query.filter_by(
                    movie_id=movie_id,
                    user_id=current_user_id
                ).first()
                
                if existing_rating:
                    debug_info['existing_rating'] = {
                        'id': str(existing_rating.id),
                        'rating': existing_rating.rating,
                        'comment': existing_rating.comment,
                        'created_at': existing_rating.created_at.isoformat() if existing_rating.created_at else None
                    }
                else:
                    debug_info['existing_rating'] = None
        
        # Database connectivity test
        try:
            db.session.execute(text('SELECT 1'))
            debug_info['database_connection'] = 'OK'
        except Exception as e:
            debug_info['database_connection'] = f'ERROR: {str(e)}'
            issues.append(f"Database connection issue: {str(e)}")
            can_rate = False
        
        # Environment info
        debug_info['environment'] = {
            'api_environment': current_app.config.get('API_ENVIRONMENT'),
            'log_level': current_app.config.get('LOG_LEVEL'),
            'database_url_prefix': str(current_app.config.get('SQLALCHEMY_DATABASE_URI', ''))[:30] + '...'
        }
        
        return jsonify({
            'debug_info': debug_info,
            'can_rate': can_rate,
            'issues': issues,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"🔧 Debug endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'movie_id': movie_id
        }), 500

@dev_bp.route('/debug/validate-rating', methods=['POST'])
def debug_validate_rating():
    """Debug endpoint to test rating validation
    ---
    tags:
      - Development
    summary: Debug rating validation
    description: Test rating validation logic
    parameters:
      - in: body
        name: test_data
        required: true
        schema:
          type: object
          properties:
            rating:
              type: any
              description: Rating value to test
    responses:
      200:
        description: Validation results
    """
    try:
        data = request.get_json() or {}
        test_rating = data.get('rating')
        
        validation_result = validate_rating(test_rating)
        
        return jsonify({
            'input_value': test_rating,
            'input_type': type(test_rating).__name__,
            'is_valid': validation_result,
            'validation_details': {
                'converted_to_int': None,
                'in_range_1_10': None,
                'error': None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@dev_bp.route('/debug/logs', methods=['GET'])
def debug_logs():
    """Debug endpoint to check logging configuration
    ---
    tags:
      - Development
    summary: Debug logging
    description: Check current logging configuration and test log output
    responses:
      200:
        description: Logging information
    """
    import logging
    
    try:
        # Test different log levels
        current_app.logger.debug("🔧 DEBUG: This is a debug message")
        current_app.logger.info("🔧 INFO: This is an info message")
        current_app.logger.warning("🔧 WARNING: This is a warning message")
        current_app.logger.error("🔧 ERROR: This is an error message")
        
        # Get logging configuration
        root_logger = logging.getLogger()
        
        handlers_info = []
        for handler in root_logger.handlers:
            handlers_info.append({
                'type': type(handler).__name__,
                'level': handler.level,
                'level_name': logging.getLevelName(handler.level)
            })
        
        return jsonify({
            'logging_config': {
                'root_level': root_logger.level,
                'root_level_name': logging.getLevelName(root_logger.level),
                'app_logger_level': current_app.logger.level,
                'app_logger_level_name': logging.getLevelName(current_app.logger.level),
                'handlers': handlers_info,
                'config_log_level': current_app.config.get('LOG_LEVEL'),
                'environment': current_app.config.get('API_ENVIRONMENT')
            },
            'test_messages_sent': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500
