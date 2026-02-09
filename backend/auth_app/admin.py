"""
Authentication Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, OTPRecord, LoginAttempt, GoogleAuthToken


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile Admin"""
    
    list_display = [
        'user_link',
        'email',
        'email_verified_badge',
        'admin_badge',
        'google_badge',
        'login_count',
        'created_at'
    ]
    
    list_filter = ['is_email_verified', 'is_admin_user', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'login_count']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number')
        }),
        ('Verification Status', {
            'fields': ('is_email_verified', 'is_admin_user')
        }),
        ('Google Integration', {
            'fields': ('google_id', 'profile_picture')
        }),
        ('Security', {
            'fields': ('last_login_ip', 'login_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'Username'
    
    def email(self, obj):
        return obj.user.email
    
    def email_verified_badge(self, obj):
        if obj.is_email_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Not Verified</span>'
        )
    email_verified_badge.short_description = 'Email Status'
    
    def admin_badge(self, obj):
        if obj.is_admin_user:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 10px; border-radius: 3px;">Admin</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">User</span>'
        )
    admin_badge.short_description = 'Role'
    
    def google_badge(self, obj):
        if obj.google_id:
            return format_html(
                '<span style="background-color: #4285f4; color: white; padding: 3px 10px; border-radius: 3px;">🌐 Google</span>'
            )
        return '—'
    google_badge.short_description = 'OAuth'


@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    """OTP Record Admin"""
    
    list_display = [
        'email',
        'otp_display',
        'purpose',
        'status_badge',
        'attempts_display',
        'created_at',
        'expires_at'
    ]
    
    list_filter = ['purpose', 'is_verified', 'created_at']
    search_fields = ['email', 'temp_username']
    readonly_fields = [
        'otp_code',
        'created_at',
        'verified_at',
        'attempts',
        'is_verified'
    ]
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('email', 'otp_code', 'purpose')
        }),
        ('User Data', {
            'fields': ('temp_username', 'temp_first_name', 'temp_last_name')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'verified_at', 'attempts', 'max_attempts')
        }),
        ('Validity', {
            'fields': ('created_at', 'expires_at')
        }),
        ('Security', {
            'fields': ('ip_address',)
        }),
    )
    
    def otp_display(self, obj):
        return format_html(
            '<code style="background-color: #f8f9fa; padding: 5px 10px; border-radius: 3px; font-size: 14px; font-weight: bold;">{}</code>',
            obj.otp_code
        )
    otp_display.short_description = 'OTP Code'
    
    def status_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Verified</span>'
            )
        elif obj.is_expired():
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">⏰ Expired</span>'
            )
        elif obj.attempts >= obj.max_attempts:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">🚫 Max Attempts</span>'
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px;">⏳ Pending</span>'
        )
    status_badge.short_description = 'Status'
    
    def attempts_display(self, obj):
        color = '#28a745' if obj.attempts == 0 else '#ffc107' if obj.attempts < obj.max_attempts else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{}</span>',
            color,
            obj.attempts,
            obj.max_attempts
        )
    attempts_display.short_description = 'Attempts'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Login Attempt Admin"""
    
    list_display = [
        'username_or_email',
        'status_badge',
        'ip_address',
        'attempted_at',
        'failure_reason'
    ]
    
    list_filter = ['success', 'attempted_at']
    search_fields = ['username_or_email', 'ip_address']
    readonly_fields = ['username_or_email', 'ip_address', 'success', 'failure_reason', 'attempted_at', 'user_agent']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('username_or_email', 'success', 'failure_reason')
        }),
        ('Security Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('attempted_at',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.success:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Success</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Failed</span>'
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(GoogleAuthToken)
class GoogleAuthTokenAdmin(admin.ModelAdmin):
    """Google Auth Token Admin"""
    
    list_display = [
        'user',
        'token_type',
        'expires_at',
        'status_badge',
        'created_at'
    ]
    
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Token Information', {
            'fields': ('access_token', 'refresh_token', 'token_type', 'scope')
        }),
        ('Validity', {
            'fields': ('expires_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">⏰ Expired</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active</span>'
        )
    status_badge.short_description = 'Status'
