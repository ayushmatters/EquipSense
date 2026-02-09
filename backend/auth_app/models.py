"""
Authentication Models
Extended User Profile and OTP Management
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['google_id']),
            models.Index(fields=['is_email_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def increment_login_count(self):
        """Increment login counter"""
        self.login_count += 1
        self.save(update_fields=['login_count'])


class OTPRecord(models.Model):
    """OTP verification records"""
    
    OTP_PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
    ]
    
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=OTP_PURPOSE_CHOICES, default='registration')
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Additional registration data
    temp_username = models.CharField(max_length=150, blank=True, null=True)
    temp_first_name = models.CharField(max_length=150, blank=True, null=True)
    temp_last_name = models.CharField(max_length=150, blank=True, null=True)
    
    class Meta:
        db_table = 'otp_records'
        verbose_name = 'OTP Record'
        verbose_name_plural = 'OTP Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_verified']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.otp_code}"
    
    @staticmethod
    def generate_otp():
        """Generate 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if OTP is expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and not self.is_expired() and self.attempts < self.max_attempts
    
    def verify(self, otp_code):
        """Verify OTP code"""
        self.attempts += 1
        
        if not self.is_valid():
            return False, "OTP expired or maximum attempts reached"
        
        if self.otp_code == otp_code:
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
            return True, "OTP verified successfully"
        
        self.save()
        remaining = self.max_attempts - self.attempts
        return False, f"Invalid OTP. {remaining} attempts remaining"
    
    @classmethod
    def create_otp(cls, email, purpose='registration', validity_minutes=5, **extra_data):
        """Create new OTP record"""
        # Invalidate previous OTPs for same email and purpose
        cls.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).update(is_verified=True)  # Mark as used to prevent reuse
        
        otp = cls(
            email=email,
            otp_code=cls.generate_otp(),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=validity_minutes),
            **extra_data
        )
        otp.save()
        return otp
    
    def get_remaining_time(self):
        """Get remaining validity time in seconds"""
        if self.is_expired():
            return 0
        delta = self.expires_at - timezone.now()
        return int(delta.total_seconds())


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    
    username_or_email = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'login_attempts'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['ip_address', 'attempted_at']),
            models.Index(fields=['username_or_email', 'attempted_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username_or_email} - {status} - {self.attempted_at}"
    
    @classmethod
    def is_rate_limited(cls, identifier, ip_address, max_attempts=5, time_window_minutes=15):
        """Check if IP or user is rate limited"""
        time_threshold = timezone.now() - timedelta(minutes=time_window_minutes)
        
        # Check failed attempts from this IP
        ip_attempts = cls.objects.filter(
            ip_address=ip_address,
            success=False,
            attempted_at__gte=time_threshold
        ).count()
        
        # Check failed attempts for this username/email
        user_attempts = cls.objects.filter(
            username_or_email=identifier,
            success=False,
            attempted_at__gte=time_threshold
        ).count()
        
        return ip_attempts >= max_attempts or user_attempts >= max_attempts


class GoogleAuthToken(models.Model):
    """Store Google OAuth tokens for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_token')
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    scope = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'google_auth_tokens'
        verbose_name = 'Google Auth Token'
        verbose_name_plural = 'Google Auth Tokens'
    
    def __str__(self):
        return f"{self.user.username} - Google Token"
    
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() >= self.expires_at
