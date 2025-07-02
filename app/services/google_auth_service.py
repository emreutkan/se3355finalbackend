from flask import current_app
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from ..utils.logger import get_auth_logger
import os

auth_logger = get_auth_logger()


class GoogleAuthService:
    def get_flow(self):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        auth_logger.info("Creating Google OAuth flow")
        
        # Validate required configuration
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
        
        if not client_id:
            auth_logger.error("GOOGLE_CLIENT_ID is not configured")
            return None
        if not client_secret:
            auth_logger.error("GOOGLE_CLIENT_SECRET is not configured")
            return None
        if not redirect_uri:
            auth_logger.error("GOOGLE_REDIRECT_URI is not configured")
            return None
            
        auth_logger.info(f"Using redirect_uri: {redirect_uri}")
        auth_logger.info(f"Client ID configured: {client_id[:10]}..." if client_id else "Client ID missing")
        
        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=[
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'openid'
                ],
                redirect_uri=redirect_uri
            )
            auth_logger.info(f"Successfully created Google OAuth flow with redirect_uri: {redirect_uri}")
            return flow
        except Exception as e:
            auth_logger.critical(f"Failed to create Google OAuth flow: {e}", exc_info=True)
            return None

    def get_tokens(self, authorization_response_url: str):
        auth_logger.info(f"Attempting to fetch Google OAuth tokens with response URL: {authorization_response_url}")
        
        if not authorization_response_url:
            auth_logger.error("Empty authorization response URL provided")
            return None
            
        flow = self.get_flow()
        if not flow:
            auth_logger.error("Could not create OAuth flow")
            return None
            
        try:
            # The state is not being used here, which can be a security risk.
            # For now, we proceed as is to debug the current problem.
            auth_logger.info("Calling flow.fetch_token with authorization response")
            flow.fetch_token(authorization_response=authorization_response_url)
            credentials = flow.credentials
            
            if not credentials:
                auth_logger.error("No credentials returned from flow.fetch_token")
                return None
            
            # Extracting token data to be stored or used
            tokens = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'id_token': credentials.id_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            auth_logger.info("Successfully fetched Google OAuth tokens")
            auth_logger.debug(f"Tokens received: { {k: v for k, v in tokens.items() if k != 'client_secret'} }") # Don't log secret
            return tokens
        except Exception as e:
            auth_logger.error(f"Failed to fetch Google OAuth tokens: {e}", exc_info=True)
            return None
            
    def get_user_info(self, tokens):
        auth_logger.info("Attempting to fetch user info from Google")
        if not tokens or 'token' not in tokens:
            auth_logger.error("get_user_info called with invalid or empty tokens")
            return None
        try:
            credentials = google.oauth2.credentials.Credentials(**tokens)
            
            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()
            
            auth_logger.info(f"Successfully fetched user info for email: {user_info.get('email')}")
            auth_logger.debug(f"User info received: {user_info}")
            return user_info
        except Exception as e:
            auth_logger.error(f"Failed to fetch user info from Google: {e}", exc_info=True)
            return None
