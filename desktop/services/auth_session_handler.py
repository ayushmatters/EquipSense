"""
Authentication Session Handler

Manages user authentication state and session data for the desktop application.
Integrates with frontend authentication and maintains token state.
"""

from typing import Optional, Dict
import json


class AuthSessionHandler:
    """
    Handles authentication session management for desktop application.
    
    Features:
    - Track authentication state
    - Store user information
    - Manage authentication tokens
    - Session validation
    """
    
    def __init__(self):
        self._is_authenticated = False
        self._user_data = {}
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._username = None
        self._email = None
        
    def set_authenticated(self, auth_data: Dict):
        """
        Set authentication state from login/registration.
        
        Args:
            auth_data: Dictionary containing authentication data
                Expected keys: token, user, tokens (with access/refresh)
        """
        try:
            # Extract tokens
            if 'token' in auth_data:
                self._access_token = auth_data['token']
            elif 'tokens' in auth_data:
                tokens = auth_data['tokens']
                self._access_token = tokens.get('access')
                self._refresh_token = tokens.get('refresh')
            elif 'access_token' in auth_data:
                self._access_token = auth_data['access_token']
            
            # Extract user data
            if 'user' in auth_data:
                self._user_data = auth_data['user']
                self._user_id = self._user_data.get('id')
                self._username = self._user_data.get('username')
                self._email = self._user_data.get('email')
            
            self._is_authenticated = True
            print(f"[AuthSession] User authenticated: {self._username}")
            
        except Exception as e:
            print(f"[AuthSession] Error setting authentication: {e}")
            self._is_authenticated = False
    
    def clear_session(self):
        """Clear all session data and log out user."""
        self._is_authenticated = False
        self._user_data = {}
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._username = None
        self._email = None
        print("[AuthSession] Session cleared")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self._is_authenticated and self._access_token is not None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token for API requests."""
        return self._access_token
    
    def get_refresh_token(self) -> Optional[str]:
        """Get refresh token for token renewal."""
        return self._refresh_token
    
    def get_user_data(self) -> Dict:
        """Get user data dictionary."""
        return self._user_data.copy()
    
    def get_username(self) -> Optional[str]:
        """Get authenticated username."""
        return self._username
    
    def get_user_id(self) -> Optional[int]:
        """Get authenticated user ID."""
        return self._user_id
    
    def get_email(self) -> Optional[str]:
        """Get authenticated user email."""
        return self._email
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Get authorization header for API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        if not self._access_token:
            return {}
        
        return {
            'Authorization': f'Bearer {self._access_token}'
        }
    
    def update_token(self, new_token: str):
        """
        Update access token (for token refresh).
        
        Args:
            new_token: New access token
        """
        self._access_token = new_token
        print("[AuthSession] Token updated")
    
    def get_session_info(self) -> Dict:
        """
        Get session information for debugging/display.
        
        Returns:
            Dictionary with session information
        """
        return {
            'authenticated': self._is_authenticated,
            'username': self._username,
            'email': self._email,
            'user_id': self._user_id,
            'has_access_token': self._access_token is not None,
            'has_refresh_token': self._refresh_token is not None
        }
    
    def __repr__(self) -> str:
        """String representation of session state."""
        if self._is_authenticated:
            return f"<AuthSession: {self._username} (authenticated)>"
        return "<AuthSession: (not authenticated)>"


# Global session instance
_session = None


def get_session() -> AuthSessionHandler:
    """
    Get global authentication session instance.
    
    Returns:
        AuthSessionHandler instance
    """
    global _session
    if _session is None:
        _session = AuthSessionHandler()
    return _session


def clear_global_session():
    """Clear the global session (logout)."""
    global _session
    if _session is not None:
        _session.clear_session()
