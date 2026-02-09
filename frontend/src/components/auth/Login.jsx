import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import { toast } from '../../utils/toast';
import GoogleAuthButton from './GoogleAuthButton';
import { FaUser, FaLock, FaEye, FaEyeSlash, FaShieldAlt } from 'react-icons/fa';
import '../../styles/auth.css';

const Login = () => {
    const navigate = useNavigate();
    const [loginMode, setLoginMode] = useState('user'); // 'user' or 'admin'
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    
    const [formData, setFormData] = useState({
        usernameOrEmail: '',
        username: '',
        password: '',
        rememberMe: false
    });
    
    const [errors, setErrors] = useState({});

    const handleUserLogin = async (e) => {
        e.preventDefault();
        
        if (!formData.usernameOrEmail || !formData.password) {
            toast.error('Please fill in all fields');
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.userLogin(
                formData.usernameOrEmail,
                formData.password,
                formData.rememberMe
            );
            
            if (response.success) {
                toast.success(`Welcome back, ${response.user.first_name}!`);
                navigate('/dashboard');
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Login failed';
            toast.error(errorMsg);
            setErrors({ submit: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    const handleAdminLogin = async (e) => {
        e.preventDefault();
        
        if (!formData.username || !formData.password) {
            toast.error('Please fill in all fields');
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await authService.adminLogin(
                formData.username,
                formData.password
            );
            
            if (response.success) {
                toast.success(`Welcome, Admin ${response.user.username}!`);
                navigate('/admin-dashboard');
            }
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Admin login failed';
            toast.error(errorMsg);
            setErrors({ submit: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (field, value) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: null });
        }
    };

    const switchMode = (mode) => {
        setLoginMode(mode);
        setFormData({
            usernameOrEmail: '',
            username: '',
            password: '',
            rememberMe: false
        });
        setErrors({});
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

                    {/* Login Mode Tabs */}
                    <div className="login-tabs">
                        <button
                            className={`tab-button ${loginMode === 'user' ? 'active' : ''}`}
                            onClick={() => switchMode('user')}
                        >
                            <FaUser className="tab-icon" />
                            User Login
                        </button>
                        <button
                            className={`tab-button ${loginMode === 'admin' ? 'active' : ''}`}
                            onClick={() => switchMode('admin')}
                        >
                            <FaShieldAlt className="tab-icon" />
                            Admin Login
                        </button>
                    </div>

                    {/* USER LOGIN FORM */}
                    {loginMode === 'user' && (
                        <div className="login-content fade-in">
                            <h2 className="step-title">Welcome Back</h2>
                            <p className="step-subtitle">Sign in to access your dashboard</p>

                            <form onSubmit={handleUserLogin}>
                                <div className="form-group">
                                    <label>Username or Email</label>
                                    <div className="input-with-icon">
                                        <FaUser className="input-icon" />
                                        <input
                                            type="text"
                                            placeholder="Enter username or email"
                                            value={formData.usernameOrEmail}
                                            onChange={(e) => handleInputChange('usernameOrEmail', e.target.value)}
                                            className={errors.usernameOrEmail ? 'error' : ''}
                                        />
                                    </div>
                                    {errors.usernameOrEmail && <span className="error-text">{errors.usernameOrEmail}</span>}
                                </div>

                                <div className="form-group">
                                    <label>Password</label>
                                    <div className="input-with-icon password-field">
                                        <FaLock className="input-icon" />
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            placeholder="Enter your password"
                                            value={formData.password}
                                            onChange={(e) => handleInputChange('password', e.target.value)}
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
                                    {errors.password && <span className="error-text">{errors.password}</span>}
                                </div>

                                <div className="form-options">
                                    <label className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={formData.rememberMe}
                                            onChange={(e) => handleInputChange('rememberMe', e.target.checked)}
                                        />
                                        <span>Remember me</span>
                                    </label>
                                    <a href="/auth/forgot-password" className="forgot-link">
                                        Forgot Password?
                                    </a>
                                </div>

                                {errors.submit && (
                                    <div className="alert alert-error">
                                        {errors.submit}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    className="btn-primary btn-lg"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Signing in...
                                        </>
                                    ) : (
                                        'Sign In'
                                    )}
                                </button>
                            </form>

                            <div className="divider">
                                <span>OR</span>
                            </div>

                            <GoogleAuthButton mode="signin" />

                            <div className="auth-footer">
                                <p>Don't have an account? <a href="/auth/register">Sign up</a></p>
                            </div>
                        </div>
                    )}

                    {/* ADMIN LOGIN FORM */}
                    {loginMode === 'admin' && (
                        <div className="login-content fade-in">
                            <div className="admin-badge">
                                <FaShieldAlt className="badge-icon" />
                                <span>Admin Access Only</span>
                            </div>

                            <h2 className="step-title">Admin Portal</h2>
                            <p className="step-subtitle">Secure administrative login</p>

                            <form onSubmit={handleAdminLogin}>
                                <div className="form-group">
                                    <label>Admin Username</label>
                                    <div className="input-with-icon">
                                        <FaUser className="input-icon" />
                                        <input
                                            type="text"
                                            placeholder="Enter admin username"
                                            value={formData.username}
                                            onChange={(e) => handleInputChange('username', e.target.value)}
                                            className={errors.username ? 'error' : ''}
                                        />
                                    </div>
                                    {errors.username && <span className="error-text">{errors.username}</span>}
                                </div>

                                <div className="form-group">
                                    <label>Admin Password</label>
                                    <div className="input-with-icon password-field">
                                        <FaLock className="input-icon" />
                                        <input
                                            type={showPassword ? 'text' : 'password'}
                                            placeholder="Enter admin password"
                                            value={formData.password}
                                            onChange={(e) => handleInputChange('password', e.target.value)}
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
                                    {errors.password && <span className="error-text">{errors.password}</span>}
                                </div>

                                {errors.submit && (
                                    <div className="alert alert-error">
                                        {errors.submit}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    className="btn-primary btn-lg admin-button"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Authenticating...
                                        </>
                                    ) : (
                                        <>
                                            <FaShieldAlt />
                                            Sign In as Admin
                                        </>
                                    )}
                                </button>
                            </form>

                            <div className="auth-footer">
                                <p className="admin-notice">
                                    ⚠️ Unauthorized access attempts are logged and monitored
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
    );
};

export default Login;
