"""
Custom Permissions for Admin APIs
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to check if user is an admin
    Checks: is_staff, is_superuser, or profile.is_admin_user
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is admin
        is_admin = request.user.is_staff or request.user.is_superuser
        
        if hasattr(request.user, 'profile'):
            is_admin = is_admin or request.user.profile.is_admin_user
        
        return is_admin
    
    message = 'Admin privileges required to access this endpoint'
