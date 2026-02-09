/**
 * Complete Registration Flow Component
 * Multi-step registration with OTP verification
 */

import React, { useState } from 'react';
import authService from '../../../services/authService';
import { toast } from '../../../utils/toast';
import {
    validateEmail,
    validateUsername,
    validateName,
    validatePassword,
    validateOTP,
    calculatePasswordStrength,
    maskEmail
} from '../../../utils/validation';
import '../../../styles/auth.css';

const RegisterFlow = () => {
    // State management
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    
    // Form data
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        firstName: '',
        lastName: '',
        otp: '',
        password: '',
        confirmPassword: ''
    });
    
    // Validation errors
    const [errors, setErrors] = useState({});
    
    // OTP state
    const [otpTimer, setOtpTimer] = useState(300); // 5 minutes
    const [canResendOTP, setCanResendOTP] = useState(false);
    
    // Password strength
    const [passwordStrength, setPasswordStrength] = useState({
        score: 0,
        strength: 'weak',
        color: '#ef4444',
        feedback: []
    });

    // ==========================================
    // STEP 1: Basic Details
    // ==========================================
    
    const validateStep1 = () => {
        const newErrors = {};
        
        const usernameError = validateUsername(formData.username);
        if (usernameError) newErrors.username = usernameError;
        
        const emailError = validateEmail(formData.email);
        if (emailError) newErrors.email = emailError;
        
        const firstNameError = validateName(formData.firstName, 'First name');
        if (firstNameError) newErrors.firstName = firstNameError;
        
        const lastNameError = validateName(formData.lastName, 'Last name');
        if (lastNameError) newErrors.lastName = lastNameError;
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    
    const handleSendOTP = async () => {
        if (!validateStep1()) {
            toast.error('Please fix the errors before proceeding');
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.sendOTP({
                username: formData.username,
                email: formData.email,
                firstName: formData.firstName,
                lastName: formData.lastName
            });
            
            if (response.success) {
                toast.success('OTP sent to your email!');
                setStep(2);
                startOTPTimer();
            } else {
                toast.error(response.message || 'Failed to send OTP');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Error sending OTP');
        } finally {
            setLoading(false);
        }
    };

    // ==========================================
    // STEP 2: OTP Verification
    // ==========================================
    
    const startOTPTimer = () => {
        setOtpTimer(300);
        setCanResendOTP(false);
        
        const interval = setInterval(() => {
            setOtpTimer((prev) => {
                if (prev <= 1) {
                    clearInterval(interval);
                    setCanResendOTP(true);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    };
    
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };
    
    const handleVerifyOTP = async () => {
        const otpError = validateOTP(formData.otp);
        if (otpError) {
            setErrors({ otp: otpError });
            toast.error(otpError);
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.verifyOTP(
                formData.email,
                formData.otp
            );
            
            if (response.success) {
                toast.success('OTP verified! Create your password');
                setStep(3);
            } else {
                toast.error(response.message || 'Invalid OTP');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'OTP verification failed');
        } finally {
            setLoading(false);
        }
    };
    
    const handleResendOTP = async () => {
        if (!canResendOTP) return;
        
        setLoading(true);
        
        try {
            const response = await authService.resendOTP(formData.email);
            
            if (response.success) {
                toast.success('New OTP sent!');
                startOTPTimer();
                setFormData({ ...formData, otp: '' });
            } else {
                toast.error(response.message || 'Failed to resend OTP');
            }
        } catch (error) {
            toast.error('Error resending OTP');
        } finally {
            setLoading(false);
        }
    };

    // ==========================================
    // STEP 3: Password Creation
    // ==========================================
    
    const handlePasswordChange = (password) => {
        setFormData({ ...formData, password });
        const strength = calculatePasswordStrength(password);
        setPasswordStrength(strength);
    };
    
    const handleCompleteRegistration = async () => {
        // Validate password
        const passwordError = validatePassword(formData.password);
        if (passwordError) {
            setErrors({ password: passwordError });
            toast.error('Please fix password errors');
            return;
        }
        
        // Validate confirmation
        if (formData.password !== formData.confirmPassword) {
            setErrors({ confirmPassword: 'Passwords do not match' });
            toast.error('Passwords do not match');
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.createPassword(
                formData.email,
                formData.password,
                formData.confirmPassword
            );
            
            if (response.success) {
                toast.success('Registration complete! Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
            } else {
                toast.error(response.message || 'Registration failed');
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    // ==========================================
    // RENDER
    // ==========================================
    
    return (
        <div className="auth-container">
            <div className="glass-card">
                {/* Logo */}
                <div className="auth-logo">
                    <h1>⚙️ EquipSense</h1>
                    <p>Chemical Equipment Parameter Visualizer</p>
                </div>
                
                {/* Progress Indicator */}
                <div className="progress-steps">
                    <div className={`step ${step >= 1 ? 'active' : ''}`}>1</div>
                    <div className={`step ${step >= 2 ? 'active' : ''}`}>2</div>
                    <div className={`step ${step >= 3 ? 'active' : ''}`}>3</div>
                </div>
                
                {/* Step 1: Basic Details */}
                {step === 1 && (
                    <div className="step-content fade-in">
                        <h2>Create Account</h2>
                        <p className="step-description">Enter your details to get started</p>
                        
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                placeholder="johndoe123"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                className={errors.username ? 'error' : ''}
                            />
                            {errors.username && <span className="error-text">{errors.username}</span>}
                        </div>
                        
                        <div className="form-group">
                            <label>Email Address</label>
                            <input
                                type="email"
                                placeholder="john@example.com"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className={errors.email ? 'error' : ''}
                            />
                            {errors.email && <span className="error-text">{errors.email}</span>}
                        </div>
                        
                        <div className="form-row">
                            <div className="form-group">
                                <label>First Name</label>
                                <input
                                    type="text"
                                    placeholder="John"
                                    value={formData.firstName}
                                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                                    className={errors.firstName ? 'error' : ''}
                                />
                                {errors.firstName && <span className="error-text">{errors.firstName}</span>}
                            </div>
                            
                            <div className="form-group">
                                <label>Last Name</label>
                                <input
                                    type="text"
                                    placeholder="Doe"
                                    value={formData.lastName}
                                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                                    className={errors.lastName ? 'error' : ''}
                                />
                                {errors.lastName && <span className="error-text">{errors.lastName}</span>}
                            </div>
                        </div>
                        
                        <button
                            className="gradient-button full-width"
                            onClick={handleSendOTP}
                            disabled={loading}
                        >
                            {loading ? 'Sending...' : 'Generate OTP →'}
                        </button>
                        
                        <div className="divider">OR</div>
                        
                        <button className="google-button">
                            <img src="/google-icon.svg" alt="Google" />
                            Sign up with Google
                        </button>
                        
                        <p className="auth-switch">
                            Already have an account? <a href="/auth/login">Log in</a>
                        </p>
                    </div>
                )}
                
                {/* Step 2: OTP Verification */}
                {step === 2 && (
                    <div className="step-content fade-in">
                        <h2>Verify Email</h2>
                        <p className="step-description">
                            Enter the 6-digit code sent to<br />
                            <strong>{maskEmail(formData.email)}</strong>
                        </p>
                        
                        <div className="otp-input-container">
                            {[0, 1, 2, 3, 4, 5].map((index) => (
                                <input
                                    key={index}
                                    type="text"
                                    maxLength="1"
                                    className="otp-input-box"
                                    value={formData.otp[index] || ''}
                                    onChange={(e) => {
                                        const newOTP = formData.otp.split('');
                                        newOTP[index] = e.target.value;
                                        setFormData({ ...formData, otp: newOTP.join('') });
                                        
                                        // Auto-focus next input
                                        if (e.target.value && index < 5) {
                                            e.target.nextSibling?.focus();
                                        }
                                    }}
                                    onKeyDown={(e) => {
                                        // Handle backspace
                                        if (e.key === 'Backspace' && !formData.otp[index] && index > 0) {
                                            e.target.previousSibling?.focus();
                                        }
                                    }}
                                />
                            ))}
                        </div>
                        
                        {errors.otp && <span className="error-text center">{errors.otp}</span>}
                        
                        <div className="otp-timer">
                            {otpTimer > 0 ? (
                                <span>Time remaining: <strong>{formatTime(otpTimer)}</strong></span>
                            ) : (
                                <span className="expired">OTP expired</span>
                            )}
                        </div>
                        
                        <button
                            className="gradient-button full-width"
                            onClick={handleVerifyOTP}
                            disabled={loading || formData.otp.length !== 6}
                        >
                            {loading ? 'Verifying...' : 'Verify OTP'}
                        </button>
                        
                        <button
                            className="text-button"
                            onClick={handleResendOTP}
                            disabled={!canResendOTP || loading}
                        >
                            {canResendOTP ? 'Resend OTP' : `Resend available in ${formatTime(Math.max(0, 30 - (300 - otpTimer)))}`}
                        </button>
                        
                        <button
                            className="text-button"
                            onClick={() => setStep(1)}
                        >
                            ← Change Email
                        </button>
                    </div>
                )}
                
                {/* Step 3: Password Creation */}
                {step === 3 && (
                    <div className="step-content fade-in">
                        <h2>Create Password</h2>
                        <p className="step-description">Choose a strong password for your account</p>
                        
                        <div className="form-group">
                            <label>Password</label>
                            <div className="password-input">
                                <input
                                    type="password"
                                    placeholder="Enter password"
                                    value={formData.password}
                                    onChange={(e) => handlePasswordChange(e.target.value)}
                                    className={errors.password ? 'error' : ''}
                                />
                                <button className="toggle-password">👁️</button>
                            </div>
                            
                            {formData.password && (
                                <div className="password-strength">
                                    <div className="password-strength-meter">
                                        <div
                                            className="password-strength-fill"
                                            style={{
                                                width: `${passwordStrength.score}%`,
                                                backgroundColor: passwordStrength.color
                                            }}
                                        />
                                    </div>
                                    <div className="password-strength-label">
                                        Strength: <strong style={{ color: passwordStrength.color }}>
                                            {passwordStrength.strength}
                                        </strong>
                                    </div>
                                    {passwordStrength.feedback.length > 0 && (
                                        <ul className="password-feedback">
                                            {passwordStrength.feedback.map((tip, index) => (
                                                <li key={index}>{tip}</li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            )}
                            
                            {errors.password && <span className="error-text">{errors.password}</span>}
                        </div>
                        
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input
                                type="password"
                                placeholder="Re-enter password"
                                value={formData.confirmPassword}
                                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                                className={errors.confirmPassword ? 'error' : ''}
                            />
                            {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
                        </div>
                        
                        <button
                            className="gradient-button full-width"
                            onClick={handleCompleteRegistration}
                            disabled={loading || !formData.password || !formData.confirmPassword}
                        >
                            {loading ? 'Creating Account...' : 'Complete Registration'}
                        </button>
                        
                        <button
                            className="text-button"
                            onClick={() => setStep(2)}
                        >
                            ← Back
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RegisterFlow;
