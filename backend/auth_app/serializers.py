"""
Authentication Serializers
DRF Serializers for User Registration, Login, and Profile
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile, OTPRecord
import re


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_email_verified', 'is_admin_user', 'profile_picture',
            'phone_number', 'login_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['is_email_verified', 'is_admin_user', 'login_count', 'created_at', 'updated_at']


class BasicDetailsSerializer(serializers.Serializer):
    """Step 1: Basic details validation"""
    
    username = serializers.CharField(
        max_length=150,
        min_length=3,
        required=True
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    
    def validate_username(self, value):
        """Validate username uniqueness and format"""
        # Check format: alphanumeric, underscores, hyphens only
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        
        # Check uniqueness
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        
        return value.lower()
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        
        return value.lower()
    
    def validate_first_name(self, value):
        """Validate first name"""
        if not value.strip():
            raise serializers.ValidationError("First name cannot be empty")
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name"""
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be empty")
        return value.strip()


class SendOTPSerializer(serializers.Serializer):
    """Send OTP request serializer"""
    
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    purpose = serializers.ChoiceField(
        choices=['registration', 'login', 'password_reset'],
        default='registration'
    )


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP request serializer"""
    
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=6, min_length=6, required=True)
    purpose = serializers.ChoiceField(
        choices=['registration', 'login', 'password_reset'],
        default='registration'
    )
    
    def validate_otp_code(self, value):
        """Validate OTP format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class PasswordCreationSerializer(serializers.Serializer):
    """Step 3: Password creation"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Additional custom validation
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
        
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        
        # Check if OTP is verified for this email
        otp = OTPRecord.objects.filter(
            email=data['email'],
            purpose='registration',
            is_verified=True
        ).order_by('-verified_at').first()
        
        if not otp:
            raise serializers.ValidationError({
                "email": "Email not verified. Please complete OTP verification first"
            })
        
        return data


class UserRegistrationSerializer(serializers.Serializer):
    """Complete user registration"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def create(self, validated_data):
        """Create new user from verified OTP data"""
        email = validated_data['email']
        
        # Get verified OTP record with user data
        otp = OTPRecord.objects.filter(
            email=email,
            purpose='registration',
            is_verified=True
        ).order_by('-verified_at').first()
        
        if not otp:
            raise serializers.ValidationError("No verified OTP found")
        
        # Create user
        user = User.objects.create_user(
            username=otp.temp_username,
            email=email,
            first_name=otp.temp_first_name,
            last_name=otp.temp_last_name,
            password=validated_data['password']
        )
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            is_email_verified=True
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    remember_me = serializers.BooleanField(default=False, required=False)


class AdminLoginSerializer(serializers.Serializer):
    """Admin login serializer"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class GoogleAuthSerializer(serializers.Serializer):
    """Google OAuth authentication serializer"""
    
    token = serializers.CharField(required=True)  # Google ID token
    
    def validate_token(self, value):
        """Validate Google token format"""
        if not value:
            raise serializers.ValidationError("Token cannot be empty")
        return value


class UserResponseSerializer(serializers.ModelSerializer):
    """User response with profile data"""
    
    profile = UserProfileSerializer(read_only=True)
    is_admin_user = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_admin_user', 'role', 'profile']
    
    def get_is_admin_user(self, obj):
        """Check if user is admin from profile"""
        if hasattr(obj, 'profile'):
            return obj.profile.is_admin_user
        return False
    
    def get_role(self, obj):
        """Determine user role"""
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        if hasattr(obj, 'profile') and obj.profile.is_admin_user:
            return 'admin'
        return 'user'


class PasswordStrengthSerializer(serializers.Serializer):
    """Check password strength"""
    
    password = serializers.CharField(required=True)
    
    def validate(self, data):
        """Calculate password strength score"""
        password = data['password']
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 25
        else:
            feedback.append("Use at least 8 characters")
        
        # Uppercase check
        if re.search(r'[A-Z]', password):
            score += 25
        else:
            feedback.append("Add uppercase letters")
        
        # Number check
        if re.search(r'[0-9]', password):
            score += 25
        else:
            feedback.append("Add numbers")
        
        # Special character check
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 25
        else:
            feedback.append("Add special characters")
        
        # Determine strength level
        if score >= 100:
            strength = "strong"
        elif score >= 75:
            strength = "good"
        elif score >= 50:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback
        }


# ==========================================
# PASSWORD RESET SERIALIZERS
# ==========================================

class RequestPasswordResetSerializer(serializers.Serializer):
    """Request password reset - accepts username or email"""
    
    identifier = serializers.CharField(
        required=True,
        help_text="Username or Email"
    )
    
    def validate_identifier(self, value):
        """Validate that user exists"""
        identifier = value.lower().strip()
        
        # Try to find user by username or email
        user = None
        if '@' in identifier:
            # It's an email
            user = User.objects.filter(email=identifier).first()
        else:
            # It's a username
            user = User.objects.filter(username=identifier).first()
        
        if not user:
            raise serializers.ValidationError(
                "No account found with this username or email"
            )
        
        # Check if user has verified email
        if not hasattr(user, 'profile') or not user.profile.is_email_verified:
            raise serializers.ValidationError(
                "This account's email is not verified. Please contact support."
            )
        
        return identifier


class VerifyResetOTPSerializer(serializers.Serializer):
    """Verify password reset OTP"""
    
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True
    )
    
    def validate_otp_code(self, value):
        """Validate OTP format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password with new password"""
    
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Additional custom validation
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long"
            )
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                "Password must contain at least one number"
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character"
            )
        
        return value
    
    def validate(self, data):
        """Validate password confirmation and OTP verification"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        
        # Check if OTP is verified for this email
        otp = OTPRecord.objects.filter(
            email=data['email'],
            purpose='password_reset',
            is_verified=True
        ).order_by('-verified_at').first()
        
        if not otp:
            raise serializers.ValidationError({
                "email": "Password reset not verified. Please complete OTP verification first"
            })
        
        # Check if OTP was verified recently (within 15 minutes)
        from datetime import timedelta
        from django.utils import timezone
        if timezone.now() - otp.verified_at > timedelta(minutes=15):
            raise serializers.ValidationError({
                "email": "Password reset session expired. Please request a new reset link"
            })
        
        return data
