import requests
from flask import current_app
from typing import Optional, Dict
from flask_jwt_extended import create_access_token, create_refresh_token

from ..models import db, User
from ..utils.logger import get_auth_logger, log_database_operation, log_auth_event
from ..utils.validators import validate_password
from werkzeug.utils import secure_filename
import os

auth_logger = get_auth_logger()

class AuthService:
    """Authentication service for handling OAuth and token management"""
    
    def __init__(self):
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def verify_google_token(self, token: str) -> Optional[Dict]:
        """
        Verify Google OAuth token and return user information
        
        Args:
            token: Google OAuth access token
            
        Returns:
            Dict containing user info if valid, None if invalid
        """
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(self.google_userinfo_url, headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'email': user_info.get('email'),
                    'name': user_info.get('name'),
                    'picture': user_info.get('picture'),
                    'verified_email': user_info.get('verified_email', False)
                }
            else:
                current_app.logger.error(f"Google token verification failed: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error verifying Google token: {str(e)}")
            return None
    
    def blacklist_token(self, jti: str) -> bool:
        """
        Add JWT token to blacklist (Redis implementation)
        
        Args:
            jti: JWT token identifier
            
        Returns:
            True if successfully blacklisted, False otherwise
        """
        try:
            # In a real implementation, you would store this in Redis
            # redis_client.setex(f"blacklist_{jti}", token_expire_time, "true")
            
            # For now, just log the action
            current_app.logger.info(f"Token {jti} added to blacklist")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error blacklisting token: {str(e)}")
            return False
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """
        Check if JWT token is blacklisted
        
        Args:
            jti: JWT token identifier
            
        Returns:
            True if blacklisted, False otherwise
        """
        try:
            # In a real implementation, you would check Redis
            # return redis_client.exists(f"blacklist_{jti}")
            
            # For now, always return False (no tokens blacklisted)
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error checking token blacklist: {str(e)}")
            return False

    def register_user(self, data: Dict, photo_file=None) -> (Optional[Dict], Optional[str]):
        """
        Register a new user with email, password, and other details.
        
        Args:
            data: Dictionary containing user registration data.
            photo_file: Optional uploaded photo file.
            
        Returns:
            A tuple of (tokens, error_message).
        """
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        country = data.get('country')
        city = data.get('city')

        # Only email and password are required
        if not email or not password:
            return None, "Email and password are required."

        if not validate_password(password):
            return None, "Password does not meet complexity requirements."

        if User.query.filter_by(email=email).first():
            return None, "User with this email already exists."

        photo_url = None
        if photo_file:
            filename = secure_filename(photo_file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            photo_path = os.path.join(upload_folder, filename)
            photo_file.save(photo_path)
            photo_url = photo_path

        try:
            new_user = User(
                email=email,
                full_name=full_name or email.split('@')[0],  # Use email prefix if no full_name
                country=country.upper() if country else None,
                city=city,
                photo_url=photo_url,
                auth_provider='local'
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            log_database_operation("CREATE", "users", record_id=new_user.id)
            log_auth_event("LOCAL_REGISTRATION", user_email=email, success=True)
            auth_logger.info(f"New user {email} registered successfully.")

            access_token = create_access_token(identity=new_user.id)
            refresh_token = create_refresh_token(identity=new_user.id)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': new_user.to_dict()
            }, None

        except Exception as e:
            db.session.rollback()
            auth_logger.error(f"Error registering user {email}: {e}", exc_info=True)
            log_auth_event("LOCAL_REGISTRATION_FAILED", user_email=email, success=False, error=str(e))
            return None, "An unexpected error occurred during registration."

    def process_social_login(self, user_info: Dict, provider: str) -> Optional[Dict]:
        """
        Process social login: find or create user, then generate JWT tokens.
        
        Args:
            user_info: Dictionary containing user details from the provider.
            provider: The name of the social provider (e.g., 'google').
            
        Returns:
            A dictionary with access and refresh tokens, or None on failure.
        """
        email = user_info.get('email')
        if not email:
            auth_logger.error(f"No email found in {provider} user info.")
            return None

        auth_logger.info(f"Processing {provider} login for user: {email}")

        try:
            user = User.query.filter_by(email=email).first()

            if user:
                # User exists, update info if necessary and log them in
                auth_logger.info(f"User {email} found. Updating profile from {provider}.")
                user.full_name = user_info.get('name', user.full_name)
                user.photo_url = user_info.get('picture', user.photo_url)

                if user.auth_provider != provider:
                    auth_logger.warning(f"User {email} previously logged in with {user.auth_provider}. Updating to {provider}.")
                    user.auth_provider = provider
                
                db.session.commit()
                log_auth_event("SOCIAL_LOGIN_EXISTING_USER", user_email=email, success=True)

            else:
                # User does not exist, create a new one
                auth_logger.info(f"User {email} not found. Creating new user from {provider} info.")
                
                locale = user_info.get('locale')
                country = locale.upper() if isinstance(locale, str) and len(locale) == 2 else 'US'

                new_user_data = {
                    'email': email,
                    'full_name': user_info.get('name'),
                    'photo_url': user_info.get('picture'),
                    'auth_provider': provider,
                    'country': country,
                    'city': 'Unknown'
                }
                user = User(**new_user_data)
                db.session.add(user)
                db.session.commit()
                
                log_database_operation("CREATE", "users", record_id=user.id)
                log_auth_event("SOCIAL_LOGIN_NEW_USER", user_email=email, success=True)
                auth_logger.info(f"New user {email} created successfully.")

            # Generate JWT tokens for the user
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            auth_logger.info(f"Generated JWT tokens for user {email}.")

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }

        except Exception as e:
            auth_logger.error(f"Error processing social login for {email}: {e}", exc_info=True)
            db.session.rollback()
            log_auth_event("SOCIAL_LOGIN_FAILED", user_email=email, success=False, error=str(e))
            return None 