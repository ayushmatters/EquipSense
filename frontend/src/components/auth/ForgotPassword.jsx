import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from '../../utils/toast';
import { FaUser, FaEnvelope, FaArrowLeft, FaClock } from 'react-icons/fa';
import '../../styles/auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ForgotPassword = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [cooldown, setCooldown] = useState(0);
    const [identifier, setIdentifier] = useState('');
    const [errors, setErrors] = useState({});

    // Cooldown timer
    React.useEffect(() => {
        let timer;
        if (cooldown > 0) {
            timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
        }
        return () => clearTimeout(timer);
    }, [cooldown]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!identifier.trim()) {
            setErrors({ identifier: 'Please enter your username or email' });
            toast.error('Please enter your username or email');
            return;
        }
        
        setLoading(true);
        setErrors({});
        
        try {
            const response = await axios.post(
                `${API_BASE_URL}/api/auth/password-reset/request/`,
                { identifier: identifier.trim() }
            );
            
            if (response.data.success) {
                toast.success(response.data.message);
                
                // Navigate to verify OTP page with email
                const email = response.data.email;
                navigate('/auth/verify-reset-otp', { 
                    state: { 
                        email: email,
                        maskedEmail: email,
                        expiresIn: response.data.expires_in
                    } 
                });
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Failed to send reset link';
            const errorData = error.response?.data?.errors;
            
            if (errorData) {
                setErrors(errorData);
            }
            
            toast.error(errorMsg);
            
            // Handle rate limiting
            if (error.response?.status === 429) {
                setCooldown(30);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (value) => {
        setIdentifier(value);
        if (errors.identifier) {
            setErrors({ ...errors, identifier: null });
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
                    <h2 className="step-title">Reset Password</h2>
                    <p className="step-subtitle">
                        Enter your username or email to receive a verification code
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label>Username or Email</label>
                            <div className="input-with-icon">
                                <FaUser className="input-icon" />
                                <input
                                    type="text"
                                    placeholder="Enter your username or email"
                                    value={identifier}
                                    onChange={(e) => handleInputChange(e.target.value)}
                                    className={errors.identifier ? 'error' : ''}
                                    disabled={loading || cooldown > 0}
                                />
                            </div>
                            {errors.identifier && (
                                <span className="error-text">
                                    {typeof errors.identifier === 'string' 
                                        ? errors.identifier 
                                        : errors.identifier[0]}
                                </span>
                            )}
                        </div>

                        {/* Security Notice */}
                        <div className="info-box">
                            <FaEnvelope className="info-icon" />
                            <div className="info-content">
                                <p className="info-title">Security Notice</p>
                                <p className="info-text">
                                    We'll send a 6-digit verification code to your registered email address
                                </p>
                            </div>
                        </div>

                        {/* Cooldown Notice */}
                        {cooldown > 0 && (
                            <div className="alert alert-warning">
                                <FaClock />
                                <span>Please wait {cooldown} seconds before trying again</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn-primary btn-lg"
                            disabled={loading || cooldown > 0}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Sending Code...
                                </>
                            ) : cooldown > 0 ? (
                                <>
                                    <FaClock />
                                    Wait {cooldown}s
                                </>
                            ) : (
                                <>
                                    <FaEnvelope />
                                    Send Verification Code
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

export default ForgotPassword;
