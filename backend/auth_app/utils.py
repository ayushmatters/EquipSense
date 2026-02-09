"""
Authentication Utilities
Helper functions for JWT, IP tracking, and rate limiting
"""

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Extract client IP address from request
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Extract user agent from request
    
    Args:
        request: Django request object
        
    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def generate_jwt_tokens(user):
    """
    Generate JWT access and refresh tokens for user
    
    Args:
        user: Django User object
        
    Returns:
        dict: Dictionary containing access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['is_admin'] = hasattr(user, 'profile') and user.profile.is_admin_user
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_token_lifetime(remember_me=False):
    """
    Get token lifetime based on remember_me preference
    
    Args:
        remember_me (bool): Whether to extend token lifetime
        
    Returns:
        int: Token lifetime in seconds
    """
    if remember_me:
        return 30 * 24 * 60 * 60  # 30 days
    return 24 * 60 * 60  # 24 hours


def validate_email_format(email):
    """
    Validate email format using regex
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_email(email):
    """
    Mask email address for privacy
    Example: john.doe@example.com -> j***e@e*****e.com
    
    Args:
        email (str): Email address to mask
        
    Returns:
        str: Masked email address
    """
    try:
        local, domain = email.split('@')
        domain_name, domain_ext = domain.rsplit('.', 1)
        
        # Mask local part
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        # Mask domain name
        if len(domain_name) <= 2:
            masked_domain = domain_name[0] + '*'
        else:
            masked_domain = domain_name[0] + '*' * (len(domain_name) - 2) + domain_name[-1]
        
        return f"{masked_local}@{masked_domain}.{domain_ext}"
    except:
        return email


def format_otp_for_display(otp):
    """
    Format OTP for display with spacing
    Example: 123456 -> 123 456
    
    Args:
        otp (str): OTP code
        
    Returns:
        str: Formatted OTP
    """
    if len(otp) == 6:
        return f"{otp[:3]} {otp[3:]}"
    return otp


def calculate_password_strength(password):
    """
    Calculate password strength score
    
    Args:
        password (str): Password to evaluate
        
    Returns:
        dict: Score and feedback
    """
    import re
    
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 25
    else:
        feedback.append("Use at least 8 characters")
    
    if len(password) >= 12:
        score += 10
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 20
    else:
        feedback.append("Add uppercase letters")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 15
    
    # Number check
    if re.search(r'[0-9]', password):
        score += 20
    else:
        feedback.append("Add numbers")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 20
    else:
        feedback.append("Add special characters")
    
    # Determine strength level
    if score >= 90:
        strength = "strong"
        color = "green"
    elif score >= 70:
        strength = "good"
        color = "blue"
    elif score >= 50:
        strength = "medium"
        color = "orange"
    else:
        strength = "weak"
        color = "red"
    
    return {
        'score': min(score, 100),
        'strength': strength,
        'color': color,
        'feedback': feedback
    }


def send_otp_to_service(email, otp_code, user_data, purpose='registration'):
    """
    Send OTP to Node.js OTP service for email delivery
    
    Args:
        email (str): Recipient email
        otp_code (str): OTP code
        user_data (dict): User information
        purpose (str): OTP purpose
        
    Returns:
        tuple: (success, message)
    """
    import requests
    
    try:
        otp_service_url = getattr(settings, 'OTP_SERVICE_URL', 'http://localhost:3001/api/otp/send')
        
        payload = {
            'email': email,
            'otp': otp_code,
            'firstName': user_data.get('first_name', ''),
            'lastName': user_data.get('last_name', ''),
            'purpose': purpose
        }
        
        response = requests.post(
            otp_service_url,
            json=payload,
            timeout=10
        )
        
        logger.info(f"📧 OTP Service Response: Status={response.status_code}, Body={response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success') == True:
                logger.info(f"✅ OTP sent successfully to {email}")
                return True, "OTP sent successfully"
            else:
                logger.error(f"❌ OTP service returned success=false: {response.text}")
                return False, response_json.get('message', 'Failed to send OTP')
        else:
            logger.error(f"❌ OTP service HTTP error {response.status_code}: {response.text}")
            return False, "Failed to send OTP"
            
    except requests.exceptions.Timeout:
        logger.error("OTP service timeout")
        return False, "OTP service timeout"
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to OTP service")
        return False, "OTP service unavailable"
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        return False, str(e)


def is_strong_password(password):
    """
    Check if password meets minimum strength requirements
    
    Args:
        password (str): Password to check
        
    Returns:
        tuple: (is_strong, errors)
    """
    import re
    
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors
