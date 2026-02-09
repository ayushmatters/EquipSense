import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from '../../utils/toast';
import { FaLock, FaEye, FaEyeSlash, FaCheckCircle, FaTimesCircle, FaArrowLeft } from 'react-icons/fa';
import '../../styles/auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ResetPassword = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    
    const [formData, setFormData] = useState({
        new_password: '',
        confirm_password: ''
    });
    
    const [errors, setErrors] = useState({});
    const [passwordStrength, setPasswordStrength] = useState({
        score: 0,
        strength: 'weak',
        feedback: []
    });

    // Get email from navigation state
    const email = location.state?.email || '';
    const verified = location.state?.verified || false;

    // Redirect if not verified
    useEffect(() => {
        if (!email || !verified) {
            toast.warning('Please complete OTP verification first');
            navigate('/auth/forgot-password');
        }
    }, [email, verified, navigate]);

    // Password strength validation
    const checkPasswordStrength = (password) => {
        let score = 0;
        const feedback = [];

        if (password.length >= 8) {
            score += 25;
        } else {
            feedback.push('At least 8 characters');
        }

        if (/[A-Z]/.test(password)) {
            score += 25;
        } else {
            feedback.push('One uppercase letter');
        }

        if (/[0-9]/.test(password)) {
            score += 25;
        } else {
            feedback.push('One number');
        }

        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            score += 25;
        } else {
            feedback.push('One special character');
        }

        let strength = 'weak';
        if (score >= 100) strength = 'strong';
        else if (score >= 75) strength = 'good';
        else if (score >= 50) strength = 'medium';

        return { score, strength, feedback };
    };

    const handleInputChange = (field, value) => {
        setFormData({ ...formData, [field]: value });
        
        // Check password strength
        if (field === 'new_password') {
            const strength = checkPasswordStrength(value);
            setPasswordStrength(strength);
        }
        
        // Clear errors
        if (errors[field]) {
            setErrors({ ...errors, [field]: null });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.new_password || !formData.confirm_password) {
            toast.error('Please fill in all fields');
            return;
        }
        
        if (formData.new_password !== formData.confirm_password) {
            setErrors({ confirm_password: 'Passwords do not match' });
            toast.error('Passwords do not match');
            return;
        }
        
        if (passwordStrength.score < 100) {
            toast.error('Please create a stronger password');
            return;
        }
        
        setLoading(true);
        setErrors({});
        
        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/auth/password-reset/reset/`,
                {
                    email: email,
                    new_password: formData.new_password,
                    confirm_password: formData.confirm_password
                }
            );
            
            if (response.data.success) {
                toast.success(response.data.message);
                
                // Redirect to login after 2 seconds
                setTimeout(() => {
                    navigate('/login', { 
                        state: { 
                            message: 'Password reset successful. Please login with your new password.' 
                        } 
                    });
                }, 2000);
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Password reset failed';
            const errorData = error.response?.data?.errors;
            
            if (errorData) {
                setErrors(errorData);
            }
            
            toast.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const getStrengthColor = () => {
        switch (passwordStrength.strength) {
            case 'strong': return '#10b981';
            case 'good': return '#3b82f6';
            case 'medium': return '#f59e0b';
            default: return '#ef4444';
        }
    };

    const getStrengthLabel = () => {
        switch (passwordStrength.strength) {
            case 'strong': return 'Strong Password';
            case 'good': return 'Good Password';
            case 'medium': return 'Medium Strength';
            default: return 'Weak Password';
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
                    onClick={() => navigate('/login')}
                    type="button"
                >
                    <FaArrowLeft />
                    <span>Back to Login</span>
                </button>

                <div className="login-content fade-in">
                    <h2 className="step-title">Create New Password</h2>
                    <p className="step-subtitle">
                        Choose a strong password for your account
                    </p>

                    <form onSubmit={handleSubmit}>
                        {/* New Password */}
                        <div className="form-group">
                            <label>New Password</label>
                            <div className="input-with-icon password-field">
                                <FaLock className="input-icon" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Enter new password"
                                    value={formData.new_password}
                                    onChange={(e) => handleInputChange('new_password', e.target.value)}
                                    className={errors.new_password ? 'error' : ''}
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                            {errors.new_password && (
                                <span className="error-text">
                                    {typeof errors.new_password === 'string' 
                                        ? errors.new_password 
                                        : errors.new_password[0]}
                                </span>
                            )}
                        </div>

                        {/* Password Strength Indicator */}
                        {formData.new_password && (
                            <div className="password-strength">
                                <div className="strength-bar">
                                    <div 
                                        className="strength-fill"
                                        style={{ 
                                            width: `${passwordStrength.score}%`,
                                            backgroundColor: getStrengthColor()
                                        }}
                                    ></div>
                                </div>
                                <div className="strength-info">
                                    <span 
                                        className="strength-label"
                                        style={{ color: getStrengthColor() }}
                                    >
                                        {getStrengthLabel()}
                                    </span>
                                </div>
                                
                                {/* Password Requirements */}
                                <div className="password-requirements">
                                    <div className={`requirement ${formData.new_password.length >= 8 ? 'met' : ''}`}>
                                        {formData.new_password.length >= 8 ? <FaCheckCircle /> : <FaTimesCircle />}
                                        <span>At least 8 characters</span>
                                    </div>
                                    <div className={`requirement ${/[A-Z]/.test(formData.new_password) ? 'met' : ''}`}>
                                        {/[A-Z]/.test(formData.new_password) ? <FaCheckCircle /> : <FaTimesCircle />}
                                        <span>One uppercase letter</span>
                                    </div>
                                    <div className={`requirement ${/[0-9]/.test(formData.new_password) ? 'met' : ''}`}>
                                        {/[0-9]/.test(formData.new_password) ? <FaCheckCircle /> : <FaTimesCircle />}
                                        <span>One number</span>
                                    </div>
                                    <div className={`requirement ${/[!@#$%^&*(),.?":{}|<>]/.test(formData.new_password) ? 'met' : ''}`}>
                                        {/[!@#$%^&*(),.?":{}|<>]/.test(formData.new_password) ? <FaCheckCircle /> : <FaTimesCircle />}
                                        <span>One special character</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Confirm Password */}
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <div className="input-with-icon password-field">
                                <FaLock className="input-icon" />
                                <input
                                    type={showConfirmPassword ? 'text' : 'password'}
                                    placeholder="Confirm your password"
                                    value={formData.confirm_password}
                                    onChange={(e) => handleInputChange('confirm_password', e.target.value)}
                                    className={errors.confirm_password ? 'error' : ''}
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                >
                                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                            {errors.confirm_password && (
                                <span className="error-text">
                                    {typeof errors.confirm_password === 'string' 
                                        ? errors.confirm_password 
                                        : errors.confirm_password[0]}
                                </span>
                            )}
                            
                            {/* Password Match Indicator */}
                            {formData.confirm_password && (
                                <div className={`password-match ${formData.new_password === formData.confirm_password ? 'match' : 'no-match'}`}>
                                    {formData.new_password === formData.confirm_password ? (
                                        <>
                                            <FaCheckCircle />
                                            <span>Passwords match</span>
                                        </>
                                    ) : (
                                        <>
                                            <FaTimesCircle />
                                            <span>Passwords do not match</span>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            className="btn-primary btn-lg"
                            disabled={loading || passwordStrength.score < 100 || formData.new_password !== formData.confirm_password}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Resetting Password...
                                </>
                            ) : (
                                <>
                                    <FaCheckCircle />
                                    Reset Password
                                </>
                            )}
                        </button>
                    </form>

                    <div className="auth-footer">
                        <p>
                            Remember your password? <a href="/login">Sign in</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResetPassword;
