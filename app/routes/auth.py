import re
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from googleapiclient.discovery import build
import requests

from ..models import db, User
from ..utils.validators import validate_password, validate_email
from ..services.auth_service import AuthService
from ..services.google_auth_service import GoogleAuthService
from ..utils.logger import log_auth_event, log_database_operation, get_auth_logger

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
google_auth_service = GoogleAuthService()
auth_logger = get_auth_logger()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with local authentication
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: Create a new user account with email and password authentication
    parameters:
      - in: body
        name: user_data
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: "user@example.com"
            password:
              type: string
              minLength: 8
              example: "SecurePass123!"
            full_name:
              type: string
              example: "John Doe"
              description: "Optional - will use email prefix if not provided"
            country:
              type: string
              pattern: "^[A-Z]{2}$"
              example: "US"
              description: "Optional - ISO-3166-1 alpha-2 country code"
            city:
              type: string
              example: "New York"
              description: "Optional"
            photo_url:
              type: string
              format: uri
              example: "https://example.com/photo.jpg"
              description: "Optional - or upload photo file"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "User registered successfully"
            user:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                full_name:
                  type: string
                country:
                  type: string
                city:
                  type: string
      400:
        description: Bad request - missing fields or validation errors
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Missing required field: email"
      409:
        description: User already exists
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "User with this email already exists"
      500:
        description: Internal server error
    """
    try:
        # Accept both JSON and multipart/form-data
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            photo_file = None
        elif request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            photo_file = request.files.get('photo')
        else:
            return jsonify({'msg': 'Content-Type must be application/json or multipart/form-data'}), 400

        if not data:
            return jsonify({'msg': 'No data provided'}), 400
        
        # Basic validation on the route level - only email and password required
        required_fields = ['email', 'password']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            auth_logger.warning(f"Registration failed for IP {request.remote_addr}: {error_msg}")
            return jsonify({'msg': error_msg}), 400

        # Only check confirmPassword if it's provided (for form submissions)
        if 'confirmPassword' in data and data.get('password') != data.get('confirmPassword'):
            error_msg = "Passwords do not match."
            auth_logger.warning(f"Registration failed for IP {request.remote_addr}: {error_msg}")
            return jsonify({'msg': error_msg}), 400

        tokens, error = auth_service.register_user(data, photo_file)

        if error:
            return jsonify({'msg': error}), 400

        # On successful registration, redirect to a home page (frontend route)
        # In a pure API, we would just return the tokens
        response_data = {
            'msg': 'User registered successfully. Redirecting to home page.',
            'tokens': tokens
        }
        # A real redirect would be: return redirect(url_for('some_frontend_home_route'))
        return jsonify(response_data), 201

    except Exception as e:
        auth_logger.error(f"Registration error: {e}", exc_info=True)
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password
    ---
    tags:
      - Authentication
    summary: User login
    description: Authenticate user with email and password to receive JWT tokens
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: "user@example.com"
            password:
              type: string
              example: "SecurePass123!"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            refresh_token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            user:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                full_name:
                  type: string
                country:
                  type: string
                city:
                  type: string
      400:
        description: Missing email or password
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Email and password are required"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Invalid credentials"
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            current_app.logger.warning("Login attempt with missing credentials")
            return jsonify({'msg': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user or not user.check_password(data['password']):
            log_auth_event("LOGIN", data['email'], success=False, error="Invalid credentials")
            current_app.logger.warning(f"Failed login attempt for: {data['email']}")
            return jsonify({'msg': 'Invalid credentials'}), 401
        
        if user.auth_provider != 'local':
            log_auth_event("LOGIN", data['email'], success=False, error=f"Account linked with {user.auth_provider}")
            return jsonify({'msg': f'This account is linked with {user.auth_provider}. Please use Google to log in.'}), 400
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        log_auth_event("LOGIN", data['email'], success=True)
        current_app.logger.info(f"User {data['email']} logged in successfully")
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        log_auth_event("LOGIN", request.get_json().get('email') if request.get_json() else None, success=False, error=str(e))
        current_app.logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/google')
def google_login():
    """Generate a Google OAuth 2.0 authorization URL."""
    try:
        flow = google_auth_service.get_flow()
        if not flow:
            auth_logger.error("Failed to create Google OAuth flow.")
            return jsonify({'msg': 'Could not create Google authentication flow'}), 500
            
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store the state in the session to verify on callback
        # session['oauth_state'] = state
        
        auth_logger.info(f"Generated Google authorization URL: {authorization_url}")
        return jsonify({'authorization_url': authorization_url})

    except Exception as e:
        auth_logger.critical(f"Error generating Google auth URL: {e}", exc_info=True)
        return jsonify({'msg': 'Error generating Google authentication URL'}), 500

@auth_bp.route('/google/callback')
def google_callback():
    """Callback for Google OAuth"""
    try:
        full_url = request.url
        auth_logger.info(f"Received callback from Google. Full URL: {full_url}")
        
        auth_logger.info("Exchanging authorization code for tokens")
        tokens = google_auth_service.get_tokens(full_url)
        
        if not tokens:
            log_auth_event("GOOGLE_LOGIN", error="Failed to fetch tokens from Google")
            auth_logger.error("Failed to fetch tokens from Google, get_tokens returned None")
            return jsonify({'msg': 'Authentication failed: Could not fetch tokens'}), 401

        user_info = google_auth_service.get_user_info(tokens)
        
        if not user_info:
            log_auth_event("GOOGLE_LOGIN", error="Failed to fetch user info from Google")
            auth_logger.error("Failed to fetch user info from Google, get_user_info returned None")
            return jsonify({'msg': 'Authentication failed: Could not fetch user info'}), 401
        
        # Process social login (find or create user, generate JWT)
        login_result = auth_service.process_social_login(user_info, 'google')
        
        if not login_result:
            log_auth_event("GOOGLE_LOGIN", user_email=user_info.get('email'), success=False, error="Failed to process social login")
            auth_logger.error(f"Failed to process social login for {user_info.get('email')}")
            return jsonify({'msg': 'Failed to process login'}), 500
        
        log_auth_event("GOOGLE_LOGIN", user_email=user_info.get('email'), success=True)
        
        # Redirect to the frontend with tokens
        access_token = login_result['access_token']
        refresh_token = login_result['refresh_token']
        
        frontend_url = f"{current_app.config['FRONTEND_URL']}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        auth_logger.info(f"Redirecting to frontend: {frontend_url}")
        return redirect(frontend_url)

    except Exception as e:
        auth_logger.error(f"Google callback error: {e}", exc_info=True)
        return jsonify({'msg': 'An error occurred during Google authentication.'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token
    ---
    tags:
      - Authentication
    summary: Refresh access token
    description: Generate new access token using valid refresh token
    security:
      - Bearer: []
    responses:
      200:
        description: New access token generated
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Invalid or expired refresh token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Token has expired"
      404:
        description: User not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "User not found"
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        new_access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Refresh token error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and blacklist tokens
    ---
    tags:
      - Authentication
    summary: User logout
    description: Logout user and blacklist current JWT token
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logged out
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Successfully logged out"
      401:
        description: Invalid or missing token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Authentication token required"
      500:
        description: Internal server error
    """
    try:
        # In a production environment, you would add the JWT to a blacklist
        # For now, we'll just return a success message
        jti = get_jwt()['jti']
        
        # TODO: Add JWT to blacklist in Redis
        # auth_service.blacklist_token(jti)
        
        return jsonify({'msg': 'Successfully logged out'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile
    ---
    tags:
      - Authentication
    summary: Get current user information
    description: Retrieve the profile information of the currently authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            user:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                  example: "123e4567-e89b-12d3-a456-426614174000"
                email:
                  type: string
                full_name:
                  type: string
                country:
                  type: string
                city:
                  type: string
                photo_url:
                  type: string
                auth_provider:
                  type: string
                  enum: [local, google]
                created_at:
                  type: string
                  format: date-time
      401:
        description: Invalid or missing token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Authentication token required"
      404:
        description: User not found
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "User not found"
      500:
        description: Internal server error
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'msg': 'Internal server error'}), 500
