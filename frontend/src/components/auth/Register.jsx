import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import { toast } from '../../utils/toast';
import {
    validateEmail,
    validateUsername,
    validateName,
    validatePassword,
    validateOTP,
    calculatePasswordStrength,
    maskEmail
} from '../../utils/validation';
import StepProgressBar from './StepProgressBar';
import GoogleAuthButton from './GoogleAuthButton';
import { FaUser, FaEnvelope, FaLock, FaEye, FaEyeSlash } from 'react-icons/fa';
import '../../styles/auth.css';

const Register = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        firstName: '',
        lastName: '',
        otp: '',
        password: '',
        confirmPassword: ''
    });
    
    const [errors, setErrors] = useState({});
    const [otpTimer, setOtpTimer] = useState(300);
    const [canResendOTP, setCanResendOTP] = useState(false);
    const [otpExpiry, setOtpExpiry] = useState(null);
    const [passwordStrength, setPasswordStrength] = useState({
        score: 0,
        strength: 'weak',
        color: '#ef4444',
        feedback: []
    });

    const steps = ['User Details', 'OTP Verification', 'Password Setup'];

    // Timer effect
    React.useEffect(() => {
        if (currentStep === 2 && otpTimer > 0) {
            const timer = setInterval(() => {
                setOtpTimer(prev => {
                    if (prev <= 1) {
                        setCanResendOTP(true);
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
            return () => clearInterval(timer);
        }
    }, [currentStep, otpTimer]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // STEP 1: User Details Validation
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

    const handleGenerateOTP = async () => {
        if (!validateStep1()) {
            toast.error('Please fix all errors before continuing');
            return;
        }
        
        setLoading(true);
        console.log('📤 Sending OTP request for:', formData.email);
        
        try {
            const response = await authService.sendOTP({
                username: formData.username,
                email: formData.email,
                firstName: formData.firstName,
                lastName: formData.lastName
            });
            
            console.log('✅ Full OTP Response:', JSON.stringify(response, null, 2));
            console.log('Response type:', typeof response);
            console.log('Response.success:', response.success);
            console.log('Response.message:', response.message);
            
            if (response && response.success === true) {
                console.log('✅ OTP sent successfully! Moving to step 2');
                toast.success(`OTP sent to ${maskEmail(formData.email)}!`);
                setCurrentStep(2);
                const expiresIn = response.expires_in || 300;
                console.log('OTP expires in:', expiresIn, 'seconds');
                setOtpTimer(expiresIn);
                setOtpExpiry(new Date(Date.now() + expiresIn * 1000));
                setCanResendOTP(false);
            } else {
                const errorMsg = response?.message || 'Failed to send OTP';
                console.error('❌ OTP failed - success is not true:', response);
                toast.error(errorMsg);
                setErrors({ submit: errorMsg });
            }
        } catch (error) {
            console.error('❌ OTP Error caught:', error);
            console.error('Error type:', error.constructor.name);
            console.error('Error response:', error.response);
            console.error('Error response data:', error.response?.data);
            const errorMsg = error.response?.data?.message || error.message || 'Failed to send OTP';
            toast.error(errorMsg);
            setErrors({ submit: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    // STEP 2: OTP Verification
    const handleVerifyOTP = async () => {
        const otpError = validateOTP(formData.otp);
        if (otpError) {
            setErrors({ otp: otpError });
            toast.error(otpError);
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.verifyOTP(formData.email, formData.otp);
            
            if (response.success) {
                toast.success('✓ Email verified successfully!');
                setCurrentStep(3);
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Invalid OTP code';
            toast.error(errorMsg);
            setErrors({ otp: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    const handleResendOTP = async () => {
        if (!canResendOTP || loading) return;
        
        setLoading(true);
        
        try {
            const response = await authService.resendOTP(formData.email);
            
            if (response.success) {
                toast.success('New OTP sent!');
                const expiresIn = response.data?.expires_in || 300;
                setOtpTimer(expiresIn);
                setCanResendOTP(false);
                setFormData({ ...formData, otp: '' });
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Failed to resend OTP');
        } finally {
            setLoading(false);
        }
    };

    // STEP 3: Password Creation
    const handlePasswordChange = (password) => {
        setFormData({ ...formData, password });
        const strength = calculatePasswordStrength(password);
        setPasswordStrength(strength);
    };

    const handleCreateAccount = async () => {
        const passwordError = validatePassword(formData.password);
        if (passwordError) {
            setErrors({ password: passwordError });
            toast.error('Password does not meet requirements');
            return;
        }
        
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
                toast.success('🎉 Account created successfully!');
                
                // Show success animation then redirect
                setTimeout(() => {
                    navigate('/auth/login');
                }, 2000);
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Registration failed';
            toast.error(errorMsg);
            setErrors({ submit: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (field, value) => {
        setFormData({ ...formData, [field]: value });
        // Clear error when user starts typing
        if (errors[field]) {
            setErrors({ ...errors, [field]: null });
        }
    };

    const handleOTPInput = (index, value) => {
        if (!/^\d*$/.test(value)) return; // Only digits
        
        const otpArray = formData.otp.split('');
        otpArray[index] = value;
        const newOTP = otpArray.join('');
        
        setFormData({ ...formData, otp: newOTP });
        
        // Auto-focus next input
        if (value && index < 5) {
            const nextInput = document.getElementById(`otp-${index + 1}`);
            if (nextInput) nextInput.focus();
        }
        
        // Auto-submit when complete
        if (newOTP.length === 6) {
            setTimeout(() => handleVerifyOTP(), 300);
        }
    };

    const handleOTPKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !formData.otp[index] && index > 0) {
            const prevInput = document.getElementById(`otp-${index - 1}`);
            if (prevInput) prevInput.focus();
        }
    };

    return (
        <div className="auth-page">
            <div className="glass-card auth-card">
                {/* Logo & Branding */}
                <div className="auth-logo">
                    <div className="logo-icon">⚙️</div>
                    <h1>EquipSense</h1>
                    <p className="tagline">Chemical Equipment Parameter Visualizer</p>
                </div>

                    {/* Step Progress Bar */}
                    <StepProgressBar 
                        currentStep={currentStep} 
                        totalSteps={3} 
                        steps={steps} 
                    />

                    {/* STEP 1: User Details */}
                    {currentStep === 1 && (
                        <div className="step-content fade-in">
                            <h2 className="step-title">Create Your Account</h2>
                            <p className="step-subtitle">Enter your details to get started</p>

                            <div className="form-group">
                                <label>Username</label>
                                <div className="input-with-icon">
                                    <FaUser className="input-icon" />
                                    <input
                                        type="text"
                                        placeholder="Choose a username"
                                        value={formData.username}
                                        onChange={(e) => handleInputChange('username', e.target.value)}
                                        className={errors.username ? 'error' : ''}
                                    />
                                </div>
                                {errors.username && <span className="error-text">{errors.username}</span>}
                            </div>

                            <div className="form-group">
                                <label>Email Address</label>
                                <div className="input-with-icon">
                                    <FaEnvelope className="input-icon" />
                                    <input
                                        type="email"
                                        placeholder="your.email@example.com"
                                        value={formData.email}
                                        onChange={(e) => handleInputChange('email', e.target.value)}
                                        className={errors.email ? 'error' : ''}
                                    />
                                </div>
                                {errors.email && <span className="error-text">{errors.email}</span>}
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>First Name</label>
                                    <input
                                        type="text"
                                        placeholder="John"
                                        value={formData.firstName}
                                        onChange={(e) => handleInputChange('firstName', e.target.value)}
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
                                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                                        className={errors.lastName ? 'error' : ''}
                                    />
                                    {errors.lastName && <span className="error-text">{errors.lastName}</span>}
                                </div>
                            </div>

                            <button
                                className="btn-primary btn-lg"
                                onClick={handleGenerateOTP}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Generating OTP...
                                    </>
                                ) : (
                                    'Generate OTP →'
                                )}
                            </button>

                            <div className="divider">
                                <span>OR</span>
                            </div>

                            <GoogleAuthButton mode="signup" />

                            <div className="auth-footer">
                                <p>Already have an account? <a href="/auth/login">Log in</a></p>
                            </div>
                        </div>
                    )}

                    {/* STEP 2: OTP Verification */}
                    {currentStep === 2 && (
                        <div className="step-content fade-in">
                            <h2 className="step-title">Verify Your Email</h2>
                            <p className="step-subtitle">
                                Enter the code sent to<br/>
                                <strong className="highlight-email">{maskEmail(formData.email)}</strong>
                            </p>

                            <div className="otp-container">
                                {[0, 1, 2, 3, 4, 5].map((index) => (
                                    <input
                                        key={index}
                                        id={`otp-${index}`}
                                        type="text"
                                        maxLength="1"
                                        className="otp-box"
                                        value={formData.otp[index] || ''}
                                        onChange={(e) => handleOTPInput(index, e.target.value)}
                                        onKeyDown={(e) => handleOTPKeyDown(index, e)}
                                    />
                                ))}
                            </div>

                            {errors.otp && <span className="error-text center-text">{errors.otp}</span>}

                            <div className="otp-timer">
                                {otpTimer > 0 ? (
                                    <span>⏱️ Time remaining: <strong>{formatTime(otpTimer)}</strong></span>
                                ) : (
                                    <span className="expired">⚠️ OTP expired</span>
                                )}
                            </div>

                            <button
                                className="btn-primary btn-lg"
                                onClick={handleVerifyOTP}
                                disabled={loading || formData.otp.length !== 6}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Verifying...
                                    </>
                                ) : (
                                    'Verify OTP'
                                )}
                            </button>

                            <button
                                className="btn-text"
                                onClick={handleResendOTP}
                                disabled={!canResendOTP || loading}
                            >
                                {canResendOTP ? '🔄 Resend OTP' : `Resend available in ${formatTime(otpTimer)}`}
                            </button>

                            <button
                                className="btn-text"
                                onClick={() => setCurrentStep(1)}
                            >
                                ← Change Email
                            </button>
                        </div>
                    )}

                    {/* STEP 3: Password Setup */}
                    {currentStep === 3 && (
                        <div className="step-content fade-in">
                            <h2 className="step-title">Create Secure Password</h2>
                            <p className="step-subtitle">Choose a strong password for your account</p>

                            <div className="form-group">
                                <label>Password</label>
                                <div className="input-with-icon password-field">
                                    <FaLock className="input-icon" />
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        placeholder="Create a strong password"
                                        value={formData.password}
                                        onChange={(e) => handlePasswordChange(e.target.value)}
                                        className={errors.password ? 'error' : ''}
                                    />
                                    <button
                                        type="button"
                                        className="password-toggle"
                                        onClick={() => setShowPassword(!showPassword)}
                                    >
                                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                                    </button>
                                </div>

                                {formData.password && (
                                    <div className="password-strength-container">
                                        <div className="password-strength-bar">
                                            <div
                                                className="password-strength-fill"
                                                style={{
                                                    width: `${passwordStrength.score}%`,
                                                    backgroundColor: passwordStrength.color
                                                }}
                                            />
                                        </div>
                                        <div className="password-strength-label">
                                            <span>Strength: </span>
                                            <strong style={{ color: passwordStrength.color }}>
                                                {passwordStrength.strength.toUpperCase()}
                                            </strong>
                                        </div>
                                        {passwordStrength.feedback.length > 0 && (
                                            <ul className="password-requirements">
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
                                <div className="input-with-icon password-field">
                                    <FaLock className="input-icon" />
                                    <input
                                        type={showConfirmPassword ? 'text' : 'password'}
                                        placeholder="Re-enter your password"
                                        value={formData.confirmPassword}
                                        onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                                        className={errors.confirmPassword ? 'error' : ''}
                                    />
                                    <button
                                        type="button"
                                        className="password-toggle"
                                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    >
                                        {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                                    </button>
                                </div>
                                {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
                            </div>

                            <button
                                className="btn-primary btn-lg"
                                onClick={handleCreateAccount}
                                disabled={loading || !formData.password || !formData.confirmPassword}
                            >
                                {loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Creating Account...
                                    </>
                                ) : (
                                    '✓ Create Account'
                                )}
                            </button>

                            <button
                                className="btn-text"
                                onClick={() => setCurrentStep(2)}
                            >
                                ← Back
                            </button>
                        </div>
                    )}
                </div>
            </div>
    );
};

export default Register;
