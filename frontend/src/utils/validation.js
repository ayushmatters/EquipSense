/**
 * Form Validation Utilities
 */

export const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) return 'Email is required';
    if (!regex.test(email)) return 'Invalid email format';
    return '';
};

export const validateUsername = (username) => {
    if (!username) return 'Username is required';
    if (username.length < 3) return 'Username must be at least 3 characters';
    if (username.length > 30) return 'Username must be less than 30 characters';
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        return 'Username can only contain letters, numbers, underscores, and hyphens';
    }
    return '';
};

export const validateName = (name, fieldName = 'Name') => {
    if (!name || !name.trim()) return `${fieldName} is required`;
    if (name.trim().length < 2) return `${fieldName} must be at least 2 characters`;
    return '';
};

export const validatePassword = (password) => {
    const errors = [];
    
    if (!password) return 'Password is required';
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('One number');
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) errors.push('One special character');
    
    return errors.length > 0 ? errors.join(', ') : '';
};

export const validateOTP = (otp) => {
    if (!otp) return 'OTP is required';
    if (!/^\d{6}$/.test(otp)) return 'OTP must be 6 digits';
    return '';
};

export const calculatePasswordStrength = (password) => {
    let score = 0;
    const feedback = [];
    
    if (password.length >= 8) score += 25;
    else feedback.push('Use at least 8 characters');
    
    if (password.length >= 12) score += 10;
    
    if (/[A-Z]/.test(password)) score += 20;
    else feedback.push('Add uppercase');
    
    if (/[a-z]/.test(password)) score += 15;
    
    if (/[0-9]/.test(password)) score += 20;
    else feedback.push('Add numbers');
    
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 20;
    else feedback.push('Add special chars');
    
    let strength = 'weak';
    let color = '#ef4444';
    
    if (score >= 90) {
        strength = 'strong';
        color = '#10b981';
    } else if (score >= 70) {
        strength = 'good';
        color = '#3b82f6';
    } else if (score >= 50) {
        strength = 'medium';
        color = '#f59e0b';
    }
    
    return { score: Math.min(score, 100), strength, color, feedback };
};

export const maskEmail = (email) => {
    if (!email || !email.includes('@')) return email;
    
    const [local, domain] = email.split('@');
    const [domainName, ext] = domain.split('.');
    
    const maskedLocal = local.length <= 2 
        ? `${local[0]}*` 
        : `${local[0]}${'*'.repeat(local.length - 2)}${local[local.length - 1]}`;
    
    const maskedDomain = domainName.length <= 2
        ? `${domainName[0]}*`
        : `${domainName[0]}${'*'.repeat(domainName.length - 2)}${domainName[domainName.length - 1]}`;
    
    return `${maskedLocal}@${maskedDomain}.${ext}`;
};
