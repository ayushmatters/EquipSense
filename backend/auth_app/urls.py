"""
Authentication URL Configuration
"""

from django.urls import path
from . import views
from . import admin_views

app_name = 'auth_app'

urlpatterns = [
    # Registration flow
    path('register/validate-details/', views.validate_basic_details, name='validate_basic_details'),
    path('register/send-otp/', views.send_otp, name='send_otp'),
    path('register/verify-otp/', views.verify_otp, name='verify_otp'),
    path('register/create-password/', views.create_password, name='create_password'),
    path('register/resend-otp/', views.resend_otp, name='resend_otp'),
    
    # Login
    path('login/user/', views.user_login, name='user_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout, name='logout'),
    
    # Google OAuth
    path('google/auth/', views.google_auth, name='google_auth'),
    path('google/config/', views.google_config, name='google_config'),
    
    # Utilities
    path('password-strength/', views.check_password_strength, name='password_strength'),
    path('profile/', views.get_user_profile, name='user_profile'),
    
    # Password Reset Flow
    path('password-reset/request/', views.request_password_reset, name='request_password_reset'),
    path('password-reset/verify-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('password-reset/reset/', views.reset_password, name='reset_password'),
    
    # Admin APIs
    path('admin/dashboard-stats/', admin_views.admin_dashboard_stats, name='admin_dashboard_stats'),
    path('admin/users/', admin_views.get_all_users, name='get_all_users'),
    path('admin/users/<int:user_id>/delete/', admin_views.delete_user, name='delete_user'),
    path('admin/users/<int:user_id>/toggle-status/', admin_views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/change-role/', admin_views.change_user_role, name='change_user_role'),
]
