"""
Google OAuth Authentication Handler
Validate Google ID tokens and manage user authentication
"""

from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth.models import User
from .models import UserProfile, GoogleAuthToken
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class GoogleAuthHandler:
    """Handle Google OAuth operations"""
    
    # Pull from Django settings (env override supported)
    CLIENT_ID = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
    
    @classmethod
    def verify_google_token(cls, token):
        """
        Verify Google ID token and extract user information
        
        Args:
            token (str): Google ID token from frontend
            
        Returns:
            dict: User information if valid, None if invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                cls.CLIENT_ID
            )
            
            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error(f"Invalid token issuer: {idinfo['iss']}")
                return None
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo.get('email'),
                'email_verified': idinfo.get('email_verified', False),
                'name': idinfo.get('name', ''),
                'given_name': idinfo.get('given_name', ''),
                'family_name': idinfo.get('family_name', ''),
                'picture': idinfo.get('picture', ''),
            }
            
            logger.info(f"Successfully verified Google token for: {user_info['email']}")
            return user_info
            
        except ValueError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {str(e)}")
            return None
    
    @classmethod
    def get_or_create_user(cls, google_user_info):
        """
        Get existing user or create new user from Google information
        
        Args:
            google_user_info (dict): User information from Google
            
        Returns:
            tuple: (User object, created boolean)
        """
        google_id = google_user_info['google_id']
        email = google_user_info['email']
        
        # Check if user exists with this Google ID
        try:
            profile = UserProfile.objects.get(google_id=google_id)
            return profile.user, False
        except UserProfile.DoesNotExist:
            pass
        
        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
            
            # Link Google account to existing user
            profile = user.profile
            profile.google_id = google_id
            profile.is_email_verified = True
            profile.profile_picture = google_user_info.get('picture', '')
            profile.save()
            
            logger.info(f"Linked Google account to existing user: {email}")
            return user, False
            
        except User.DoesNotExist:
            pass
        
        # Create new user
        username = cls._generate_username(
            google_user_info.get('given_name', ''),
            google_user_info.get('family_name', ''),
            email
        )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=google_user_info.get('given_name', ''),
            last_name=google_user_info.get('family_name', ''),
        )
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            google_id=google_id,
            is_email_verified=True,
            profile_picture=google_user_info.get('picture', '')
        )
        
        logger.info(f"Created new user from Google auth: {email}")
        return user, True
    
    @classmethod
    def _generate_username(cls, first_name, last_name, email):
        """
        Generate unique username from Google user info
        
        Args:
            first_name (str): First name
            last_name (str): Last name
            email (str): Email address
            
        Returns:
            str: Unique username
        """
        # Try first name + last name
        base_username = f"{first_name}{last_name}".lower().replace(' ', '')
        
        # If empty, use email prefix
        if not base_username:
            base_username = email.split('@')[0].lower()
        
        # Remove non-alphanumeric characters
        base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')
        
        # Ensure uniqueness
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    @classmethod
    def authenticate_google_user(cls, token):
        """
        Complete Google authentication flow
        
        Args:
            token (str): Google ID token
            
        Returns:
            tuple: (User object, created boolean, error message)
        """
        # Verify token
        google_user_info = cls.verify_google_token(token)
        
        if not google_user_info:
            return None, False, "Invalid Google token"
        
        # Check email verification
        if not google_user_info.get('email_verified'):
            return None, False, "Google email not verified"
        
        # Get or create user
        try:
            user, created = cls.get_or_create_user(google_user_info)
            return user, created, None
        except Exception as e:
            logger.error(f"Error in Google authentication: {str(e)}")
            return None, False, str(e)
    
    @classmethod
    def store_google_tokens(cls, user, access_token, refresh_token=None, expires_in=3600, scope=''):
        """
        Store Google OAuth tokens for user
        
        Args:
            user (User): Django user object
            access_token (str): Google access token
            refresh_token (str): Google refresh token (optional)
            expires_in (int): Token expiry time in seconds
            scope (str): OAuth scope
        """
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        
        GoogleAuthToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token or '',
                'token_type': 'Bearer',
                'expires_at': expires_at,
                'scope': scope
            }
        )
        
        logger.info(f"Stored Google tokens for user: {user.username}")


# Configuration helper
def get_google_oauth_config():
    """
    Get Google OAuth configuration for frontend
    
    Returns:
        dict: Configuration object
    """
    return {
        'client_id': GoogleAuthHandler.CLIENT_ID,
        'redirect_uri': getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:3000/auth/google/callback'),
        'scope': 'openid email profile',
        'response_type': 'token id_token',
    }
