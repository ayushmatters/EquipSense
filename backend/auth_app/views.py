"""
Authentication API Views
Complete authentication endpoints for registration, login, OTP, and Google OAuth
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import logging

from .models import UserProfile, OTPRecord, LoginAttempt
from .serializers import (
    BasicDetailsSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    PasswordCreationSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AdminLoginSerializer,
    GoogleAuthSerializer,
    UserResponseSerializer,
    UserProfileSerializer,
    PasswordStrengthSerializer
)
from .google_auth import GoogleAuthHandler
from .utils import (
    get_client_ip,
    get_user_agent,
    generate_jwt_tokens,
    mask_email,
    send_otp_to_service
)

logger = logging.getLogger(__name__)


# ==========================================
# REGISTRATION FLOW ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_basic_details(request):
    """
    Step 1: Validate basic user details (username, email, names)
    """
    serializer = BasicDetailsSerializer(data=request.data)
    
    if serializer.is_valid():
        return Response({
            'success': True,
            'message': 'Details validated successfully',
            'data': serializer.validated_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Step 2: Send OTP to user email for verification
    """
    logger.info(f"📬 OTP Request received: {request.data}")
    serializer = SendOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"❌ Validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Validation failed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    email = data['email']
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'message': 'Email already registered'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create OTP record
    try:
        otp_record = OTPRecord.create_otp(
            email=email,
            purpose=data['purpose'],
            validity_minutes=5,
            temp_username=data['username'],
            temp_first_name=data['first_name'],
            temp_last_name=data['last_name'],
            ip_address=get_client_ip(request)
        )
        
        # Send OTP via Node.js service
        success, message = send_otp_to_service(
            email=email,
            otp_code=otp_record.otp_code,
            user_data={
                'first_name': data['first_name'],
                'last_name': data['last_name']
            },
            purpose=data['purpose']
        )
        
        if success:
            response_data = {
                'success': True,
                'message': 'OTP sent successfully',
                'email': mask_email(email),
                'expires_in': otp_record.get_remaining_time(),
                'can_resend_after': 30
            }
            logger.info(f"✅ OTP sent to {mask_email(email)} - Returning: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            error_response = {
                'success': False,
                'message': 'Failed to send OTP. Please try again.'
            }
            logger.error(f"❌ Failed to send OTP to {email}: {message} - Returning: {error_response}")
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in send_otp: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while sending OTP'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Step 3: Verify OTP code
    """
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    email = data['email']
    otp_code = data['otp_code']
    purpose = data['purpose']
    
    # Get latest OTP record for this email and purpose
    otp_record = OTPRecord.objects.filter(
        email=email,
        purpose=purpose,
        is_verified=False
    ).order_by('-created_at').first()
    
    if not otp_record:
        return Response({
            'success': False,
            'message': 'No OTP found. Please request a new one.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify OTP
    success, message = otp_record.verify(otp_code)
    
    if success:
        logger.info(f"OTP verified for {mask_email(email)}")
        return Response({
            'success': True,
            'message': message,
            'data': {
                'email': email,
                'verified': True
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_password(request):
    """
    Step 4: Create password and complete registration
    """
    serializer = PasswordCreationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        with transaction.atomic():
            # Get verified OTP record
            otp_record = OTPRecord.objects.filter(
                email=email,
                purpose='registration',
                is_verified=True
            ).order_by('-verified_at').first()
            
            if not otp_record:
                return Response({
                    'success': False,
                    'message': 'Email not verified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = User.objects.create_user(
                username=otp_record.temp_username,
                email=email,
                first_name=otp_record.temp_first_name,
                last_name=otp_record.temp_last_name,
                password=password
            )
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                is_email_verified=True
            )
            
            logger.info(f"User registered successfully: {user.username}")
            
            return Response({
                'success': True,
                'message': 'Registration completed successfully',
                'data': {
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Error in create_password: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """Resend OTP to user email"""
    email = request.data.get('email')
    purpose = request.data.get('purpose', 'registration')
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get previous OTP record for user data
    prev_otp = OTPRecord.objects.filter(
        email=email,
        purpose=purpose
    ).order_by('-created_at').first()
    
    if not prev_otp:
        return Response({
            'success': False,
            'message': 'No previous OTP request found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create new OTP
    try:
        otp_record = OTPRecord.create_otp(
            email=email,
            purpose=purpose,
            validity_minutes=5,
            temp_username=prev_otp.temp_username,
            temp_first_name=prev_otp.temp_first_name,
            temp_last_name=prev_otp.temp_last_name,
            ip_address=get_client_ip(request)
        )
        
        # Send OTP
        success, message = send_otp_to_service(
            email=email,
            otp_code=otp_record.otp_code,
            user_data={
                'first_name': prev_otp.temp_first_name,
                'last_name': prev_otp.temp_last_name
            },
            purpose=purpose
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'OTP resent successfully',
                'data': {
                    'email': mask_email(email),
                    'expires_in': otp_record.get_remaining_time()
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to resend OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in resend_otp: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# LOGIN ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    username_or_email = data['username_or_email']
    password = data['password']
    remember_me = data.get('remember_me', False)
    
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Check rate limiting
    if LoginAttempt.is_rate_limited(username_or_email, ip_address):
        return Response({
            'success': False,
            'message': 'Too many failed login attempts. Please try again later.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Try to find user by username or email
    user = None
    if '@' in username_or_email:
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            pass
    else:
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            pass
    
    # Authenticate
    if user:
        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user:
            # Check if user is admin - admins must use admin login
            is_admin = authenticated_user.is_staff or authenticated_user.is_superuser
            if hasattr(authenticated_user, 'profile'):
                is_admin = is_admin or authenticated_user.profile.is_admin_user
            
            if is_admin:
                LoginAttempt.objects.create(
                    username_or_email=username_or_email,
                    ip_address=ip_address,
                    success=False,
                    failure_reason='Admin user attempted user login',
                    user_agent=user_agent
                )
                return Response({
                    'success': False,
                    'message': 'Admin users must login through the Admin Login section'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if email is verified
            if hasattr(authenticated_user, 'profile'):
                if not authenticated_user.profile.is_email_verified:
                    LoginAttempt.objects.create(
                        username_or_email=username_or_email,
                        ip_address=ip_address,
                        success=False,
                        failure_reason='Email not verified',
                        user_agent=user_agent
                    )
                    return Response({
                        'success': False,
                        'message': 'Please verify your email before logging in'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Update profile
                authenticated_user.profile.last_login_ip = ip_address
                authenticated_user.profile.increment_login_count()
            
            # Log successful attempt
            LoginAttempt.objects.create(
                username_or_email=username_or_email,
                ip_address=ip_address,
                success=True,
                user_agent=user_agent
            )
            
            # Generate tokens
            tokens = generate_jwt_tokens(authenticated_user)
            
            # Serialize user data
            user_serializer = UserResponseSerializer(authenticated_user)
            
            logger.info(f"User login successful: {authenticated_user.username}")
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'tokens': tokens,
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
    
    # Log failed attempt
    LoginAttempt.objects.create(
        username_or_email=username_or_email,
        ip_address=ip_address,
        success=False,
        failure_reason='Invalid credentials',
        user_agent=user_agent
    )
    
    return Response({
        'success': False,
        'message': 'Invalid username/email or password'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Admin login endpoint"""
    serializer = AdminLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    username = data['username']
    password = data['password']
    
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Check rate limiting
    if LoginAttempt.is_rate_limited(username, ip_address):
        return Response({
            'success': False,
            'message': 'Too many failed login attempts. Please try again later.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Authenticate
    user = authenticate(username=username, password=password)
    
    if user:
        # Check if user has admin privileges
        is_admin = user.is_staff or user.is_superuser
        
        if hasattr(user, 'profile'):
            is_admin = is_admin or user.profile.is_admin_user
        
        if not is_admin:
            LoginAttempt.objects.create(
                username_or_email=username,
                ip_address=ip_address,
                success=False,
                failure_reason='Not an admin user',
                user_agent=user_agent
            )
            return Response({
                'success': False,
                'message': 'You do not have admin privileges'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Update profile
        if hasattr(user, 'profile'):
            user.profile.last_login_ip = ip_address
            user.profile.increment_login_count()
        
        # Log successful attempt
        LoginAttempt.objects.create(
            username_or_email=username,
            ip_address=ip_address,
            success=True,
            user_agent=user_agent
        )
        
        # Generate tokens
        tokens = generate_jwt_tokens(user)
        
        # Serialize user data
        user_serializer = UserResponseSerializer(user)
        
        logger.info(f"Admin login successful: {user.username}")
        
        return Response({
            'success': True,
            'message': 'Admin login successful',
            'tokens': tokens,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    # Log failed attempt
    LoginAttempt.objects.create(
        username_or_email=username,
        ip_address=ip_address,
        success=False,
        failure_reason='Invalid credentials',
        user_agent=user_agent
    )
    
    return Response({
        'success': False,
        'message': 'Invalid username or password'
    }, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================
# GOOGLE OAUTH ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """Google OAuth authentication endpoint"""
    serializer = GoogleAuthSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    token = serializer.validated_data['token']
    
    # Authenticate with Google
    user, created, error = GoogleAuthHandler.authenticate_google_user(token)
    
    if error:
        return Response({
            'success': False,
            'message': error
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user:
        return Response({
            'success': False,
            'message': 'Authentication failed'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Update profile
    ip_address = get_client_ip(request)
    if hasattr(user, 'profile'):
        user.profile.last_login_ip = ip_address
        user.profile.increment_login_count()
    
    # Generate tokens
    tokens = generate_jwt_tokens(user)
    
    # Serialize user data
    user_serializer = UserResponseSerializer(user)
    
    action = "registered" if created else "logged in"
    logger.info(f"Google auth successful: {user.username} {action}")
    
    return Response({
        'success': True,
        'message': f'Google authentication successful',
        'new_user': created,
        'tokens': tokens,
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_config(request):
    """Get Google OAuth configuration for frontend"""
    from .google_auth import get_google_oauth_config
    
    config = get_google_oauth_config()
    
    return Response({
        'success': True,
        'config': config
    }, status=status.HTTP_200_OK)


# ==========================================
# UTILITY ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def check_password_strength(request):
    """Check password strength"""
    serializer = PasswordStrengthSerializer(data=request.data)
    
    if serializer.is_valid():
        strength_data = serializer.validated_data
        return Response({
            'success': True,
            'data': strength_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get authenticated user profile"""
    user_serializer = UserResponseSerializer(request.user)
    
    return Response({
        'success': True,
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user (client should delete tokens)"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)


# ==========================================
# PASSWORD RESET FLOW ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Step 1: Request password reset
    Accepts username or email, sends OTP to registered email
    """
    try:
        from .serializers import RequestPasswordResetSerializer
        from datetime import timedelta
        
        serializer = RequestPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        identifier = serializer.validated_data['identifier'].lower().strip()
        
        # Find user by username or email
        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()
        
        if not user:
            return Response({
                'success': False,
                'message': 'No account found with this username or email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        email = user.email
        
        # Rate limiting: Check if recent OTP was sent (within 30 seconds)
        recent_otp = OTPRecord.objects.filter(
            email=email,
            purpose='password_reset',
            created_at__gte=timezone.now() - timedelta(seconds=30)
        ).first()
        
        if recent_otp:
            remaining_time = 30 - int((timezone.now() - recent_otp.created_at).total_seconds())
            return Response({
                'success': False,
                'message': f'Please wait {remaining_time} seconds before requesting another reset'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create OTP record with 10 minute validity
        otp_record = OTPRecord.create_otp(
            email=email,
            purpose='password_reset',
            validity_minutes=10,
            ip_address=get_client_ip(request),
            temp_username=user.username,
            temp_first_name=user.first_name,
            temp_last_name=user.last_name
        )
        
        # Send OTP via email service
        email_sent = send_otp_to_service(
            email=email,
            otp=otp_record.otp_code,
            first_name=user.first_name,
            last_name=user.last_name,
            purpose='password_reset'
        )
        
        if not email_sent:
            logger.error(f"Failed to send password reset OTP to {mask_email(email)}")
            return Response({
                'success': False,
                'message': 'Failed to send verification email. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Password reset OTP sent to {mask_email(email)}")
        
        return Response({
            'success': True,
            'message': 'Password reset OTP sent to your email',
            'email': mask_email(email),
            'expires_in': otp_record.get_remaining_time()
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    """
    Step 2: Verify password reset OTP
    Validates OTP for password reset
    """
    try:
        from .serializers import VerifyResetOTPSerializer
        
        serializer = VerifyResetOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email'].lower()
        otp_code = serializer.validated_data['otp_code']
        
        # Get the latest valid OTP
        otp_record = OTPRecord.objects.filter(
            email=email,
            purpose='password_reset',
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_record:
            return Response({
                'success': False,
                'message': 'No password reset request found. Please request a new one.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if OTP is expired
        if otp_record.is_expired():
            return Response({
                'success': False,
                'message': 'OTP has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check max attempts
        if otp_record.attempts >= otp_record.max_attempts:
            return Response({
                'success': False,
                'message': 'Maximum verification attempts exceeded. Please request a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        success, message = otp_record.verify(otp_code)
        
        if success:
            logger.info(f"Password reset OTP verified for {mask_email(email)}")
            return Response({
                'success': True,
                'message': 'OTP verified successfully. You can now reset your password.',
                'email': email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Password reset OTP verification error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during verification'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Step 3: Reset password
    Updates user password after OTP verification
    """
    try:
        from .serializers import ResetPasswordSerializer
        
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email'].lower()
        new_password = serializer.validated_data['new_password']
        
        # Get the verified OTP record
        otp_record = OTPRecord.objects.filter(
            email=email,
            purpose='password_reset',
            is_verified=True
        ).order_by('-verified_at').first()
        
        if not otp_record:
            return Response({
                'success': False,
                'message': 'Password reset not verified. Please complete OTP verification first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Invalidate all password reset OTPs for this email
        OTPRecord.objects.filter(
            email=email,
            purpose='password_reset'
        ).update(is_verified=True)
        
        logger.info(f"Password reset successful for {mask_email(email)}")
        
        return Response({
            'success': True,
            'message': 'Password reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while resetting password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
