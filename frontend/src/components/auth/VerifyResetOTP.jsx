import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from '../../utils/toast';
import { FaShieldAlt, FaArrowLeft, FaClock, FaRedo } from 'react-icons/fa';
import '../../styles/auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const VerifyResetOTP = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [errors, setErrors] = useState({});
    const [timeRemaining, setTimeRemaining] = useState(600); // 10 minutes
    const [resendCooldown, setResendCooldown] = useState(0);
    
    const inputRefs = useRef([]);
    
    // Get email from navigation state
    const email = location.state?.email || '';
    const maskedEmail = location.state?.maskedEmail || email;

    // Redirect if no email provided
    useEffect(() => {
        if (!email) {
            toast.warning('Please request password reset first');
            navigate('/auth/forgot-password');
        }
    }, [email, navigate]);

    // Countdown timers
    useEffect(() => {
        const interval = setInterval(() => {
            setTimeRemaining((prev) => {
                if (prev <= 0) {
                    clearInterval(interval);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    // Resend cooldown timer
    useEffect(() => {
        let timer;
        if (resendCooldown > 0) {
            timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
        }
        return () => clearTimeout(timer);
    }, [resendCooldown]);

    // Focus first input on mount
    useEffect(() => {
        if (inputRefs.current[0]) {
            inputRefs.current[0].focus();
        }
    }, []);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleOtpChange = (index, value) => {
        // Allow only digits
        if (value && !/^\d+$/.test(value)) return;
        
        const newOtp = [...otp];
        newOtp[index] = value.slice(-1); // Take only last character
        setOtp(newOtp);
        
        // Auto-focus next input
        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
        
        // Clear errors
        if (errors.otp_code) {
            setErrors({ ...errors, otp_code: null });
        }
    };

    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === 'ArrowLeft' && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === 'ArrowRight' && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        const newOtp = [...otp];
        
        for (let i = 0; i < pastedData.length && i < 6; i++) {
            newOtp[i] = pastedData[i];
        }
        
        setOtp(newOtp);
        
        // Focus last filled input or first empty
        const focusIndex = Math.min(pastedData.length, 5);
        inputRefs.current[focusIndex]?.focus();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const otpCode = otp.join('');
        
        if (otpCode.length !== 6) {
            setErrors({ otp_code: 'Please enter complete 6-digit code' });
            toast.error('Please enter complete 6-digit code');
            return;
        }
        
        if (timeRemaining <= 0) {
            toast.error('OTP has expired. Please request a new one.');
            navigate('/auth/forgot-password');
            return;
        }
        
        setLoading(true);
        setErrors({});
        
        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/auth/password-reset/verify-otp/`,
                { 
                    email: email,
                    otp_code: otpCode 
                }
            );
            
            if (response.data.success) {
                toast.success(response.data.message);
                
                // Navigate to reset password page
                navigate('/auth/reset-password', { 
                    state: { 
                        email: email,
                        verified: true
                    } 
                });
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Verification failed';
            const errorData = error.response?.data?.errors;
            
            if (errorData) {
                setErrors(errorData);
            }
            
            toast.error(errorMsg);
            
            // Clear OTP on error
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        } finally {
            setLoading(false);
        }
    };

    const handleResendOTP = async () => {
        if (resendCooldown > 0) return;
        
        setResending(true);
        
        try {
            // Use the identifier (email) to resend
            const response = await axios.post(
                `${API_BASE_URL}/api/auth/password-reset/request/`,
                { identifier: email }
            );
            
            if (response.data.success) {
                toast.success('New verification code sent to your email');
                setTimeRemaining(600); // Reset to 10 minutes
                setResendCooldown(30); // 30 second cooldown
                setOtp(['', '', '', '', '', '']);
                inputRefs.current[0]?.focus();
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to resend code';
            toast.error(errorMsg);
        } finally {
            setResending(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="glass-card auth-card login-card">
                {/* Logo & Branding */}
                <div className="auth-logo">
                    <div className="logo-icon">⚙️</div>
                    <h1>EquipSense</h1>
                    <p className="tagline">Chemical Equipment Parameter Visualizer</p>
                </div>

                {/* Back Button */}
                <button 
                    className="back-button"
                    onClick={() => navigate('/auth/forgot-password')}
                    type="button"
                >
                    <FaArrowLeft />
                    <span>Back</span>
                </button>

                <div className="login-content fade-in">
                    <div className="verification-header">
                        <div className="verification-icon">
                            <FaShieldAlt />
                        </div>
                        <h2 className="step-title">Verify Your Email</h2>
                        <p className="step-subtitle">
                            We've sent a 6-digit code to<br />
                            <strong>{maskedEmail}</strong>
                        </p>
                    </div>

                    <form onSubmit={handleSubmit}>
                        {/* OTP Input Fields */}
                        <div className="otp-container">
                            {otp.map((digit, index) => (
                                <input
                                    key={index}
                                    ref={(el) => (inputRefs.current[index] = el)}
                                    type="text"
                                    inputMode="numeric"
                                    maxLength="1"
                                    className={`otp-input ${errors.otp_code ? 'error' : ''} ${digit ? 'filled' : ''}`}
                                    value={digit}
                                    onChange={(e) => handleOtpChange(index, e.target.value)}
                                    onKeyDown={(e) => handleKeyDown(index, e)}
                                    onPaste={index === 0 ? handlePaste : undefined}
                                    disabled={loading || timeRemaining <= 0}
                                />
                            ))}
                        </div>

                        {errors.otp_code && (
                            <span className="error-text centered">
                                {typeof errors.otp_code === 'string' 
                                    ? errors.otp_code 
                                    : errors.otp_code[0]}
                            </span>
                        )}

                        {/* Timer */}
                        <div className={`otp-timer ${timeRemaining <= 60 ? 'warning' : ''}`}>
                            <FaClock />
                            <span>Code expires in {formatTime(timeRemaining)}</span>
                        </div>

                        {/* Resend OTP */}
                        <div className="resend-container">
                            <p>Didn't receive the code?</p>
                            <button
                                type="button"
                                className="resend-button"
                                onClick={handleResendOTP}
                                disabled={resending || resendCooldown > 0}
                            >
                                {resending ? (
                                    <>
                                        <span className="spinner-small"></span>
                                        Sending...
                                    </>
                                ) : resendCooldown > 0 ? (
                                    <>Wait {resendCooldown}s</>
                                ) : (
                                    <>
                                        <FaRedo />
                                        Resend Code
                                    </>
                                )}
                            </button>
                        </div>

                        <button
                            type="submit"
                            className="btn-primary btn-lg"
                            disabled={loading || otp.join('').length !== 6 || timeRemaining <= 0}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Verifying...
                                </>
                            ) : (
                                <>
                                    <FaShieldAlt />
                                    Verify Code
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default VerifyResetOTP;
