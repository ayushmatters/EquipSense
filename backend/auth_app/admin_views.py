"""
Admin API Views
Endpoints for admin dashboard and user management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import logging

from .models import UserProfile, LoginAttempt
from .serializers import UserResponseSerializer, UserProfileSerializer
from .permissions import IsAdminUser

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard_stats(request):
    """
    Get admin dashboard statistics
    Returns real-time data from database
    """
    try:
        # Total Users (excluding admins)
        # Get all users who are NOT admin (not staff, not superuser, and profile is not admin)
        admin_users_ids = set()
        
        # Add staff and superusers
        admin_users_ids.update(
            User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).values_list('id', flat=True)
        )
        
        # Add users with admin profiles
        admin_profile_ids = UserProfile.objects.filter(
            is_admin_user=True
        ).values_list('user_id', flat=True)
        admin_users_ids.update(admin_profile_ids)
        
        # Count total users excluding all admin types
        total_users = User.objects.exclude(id__in=admin_users_ids).count()
        
        # Active Sessions (users who logged in within last 24 hours)
        last_24_hours = timezone.now() - timedelta(hours=24)
        active_sessions = LoginAttempt.objects.filter(
            success=True,
            attempted_at__gte=last_24_hours
        ).values('username_or_email').distinct().count()
        
        # Total Admins (staff + superuser + admin profiles, deduplicated)
        total_admins = len(admin_users_ids)
        
        # Verified Users (only count users with profiles)
        verified_users = UserProfile.objects.filter(
            is_email_verified=True
        ).count()
        
        # Recent Registrations (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        recent_registrations = User.objects.filter(
            date_joined__gte=last_week
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'totalUsers': total_users,
                'activeSessions': active_sessions,
                'systemStatus': 'online',
                'totalAdmins': total_admins,
                'verifiedUsers': verified_users,
                'recentRegistrations': recent_registrations
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in admin_dashboard_stats: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to fetch statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_users(request):
    """
    Get all registered users with their profiles
    Admin only endpoint
    """
    try:
        # Get query parameters
        role_filter = request.GET.get('role', None)  # 'user' or 'admin'
        search = request.GET.get('search', None)
        
        # Base query
        users = User.objects.select_related('profile').all()
        
        # Filter by role
        if role_filter == 'admin':
            users = users.filter(
                Q(is_staff=True) | Q(is_superuser=True) | Q(profile__is_admin_user=True)
            ).distinct()
        elif role_filter == 'user':
            users = users.filter(
                Q(is_staff=False) & Q(is_superuser=False)
            ).exclude(profile__is_admin_user=True)
        
        # Search filter
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Serialize data
        users_data = []
        for user in users:
            # Determine role
            is_admin = user.is_staff or user.is_superuser
            if hasattr(user, 'profile'):
                is_admin = is_admin or user.profile.is_admin_user
            
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': 'admin' if is_admin else 'user',
                'is_active': user.is_active,
                'is_verified': user.profile.is_email_verified if hasattr(user, 'profile') else False,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.profile.login_count if hasattr(user, 'profile') else 0,
            }
            users_data.append(user_dict)
        
        return Response({
            'success': True,
            'data': users_data,
            'total': len(users_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_all_users: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to fetch users'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, user_id):
    """Delete a user (Admin only)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent self-deletion
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'You cannot delete your own account'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Prevent deleting other admins
        if user.is_staff or user.is_superuser:
            return Response({
                'success': False,
                'message': 'Cannot delete admin users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        username = user.username
        user.delete()
        
        logger.info(f"User {username} deleted by admin {request.user.username}")
        
        return Response({
            'success': True,
            'message': f'User {username} deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to delete user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggle_user_status(request, user_id):
    """Enable/Disable a user (Admin only)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent self-disable
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'You cannot disable your own account'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Toggle status
        user.is_active = not user.is_active
        user.save()
        
        status_text = 'enabled' if user.is_active else 'disabled'
        logger.info(f"User {user.username} {status_text} by admin {request.user.username}")
        
        return Response({
            'success': True,
            'message': f'User {user.username} {status_text} successfully',
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in toggle_user_status: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to update user status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_user_role(request, user_id):
    """Change user role (Admin only)"""
    try:
        user = User.objects.get(id=user_id)
        new_role = request.data.get('role')
        
        if new_role not in ['user', 'admin']:
            return Response({
                'success': False,
                'message': 'Invalid role. Must be "user" or "admin"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent self-demotion
        if user.id == request.user.id:
            return Response({
                'success': False,
                'message': 'You cannot change your own role'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Update role
        if new_role == 'admin':
            user.is_staff = True
            if hasattr(user, 'profile'):
                user.profile.is_admin_user = True
                user.profile.save()
        else:
            user.is_staff = False
            user.is_superuser = False
            if hasattr(user, 'profile'):
                user.profile.is_admin_user = False
                user.profile.save()
        
        user.save()
        
        logger.info(f"User {user.username} role changed to {new_role} by admin {request.user.username}")
        
        return Response({
            'success': True,
            'message': f'User {user.username} role changed to {new_role}',
            'role': new_role
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in change_user_role: {str(e)}")
        return Response({
            'success': False,
            'message': 'Failed to change user role'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
