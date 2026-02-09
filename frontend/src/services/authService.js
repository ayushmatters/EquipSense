/**
 * Authentication Service
 * API calls for registration, login, and Googleauth
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const AUTH_URL = `${API_BASE_URL}/auth`;

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: AUTH_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Add auth token to requests if available
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle response errors
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired, try refresh or logout
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

const authService = {
    /**
     * Validate basic details (Step 1)
     */
    validateBasicDetails: async (data) => {
        const response = await apiClient.post('/register/validate-details/', data);
        return response.data;
    },

    /**
     * Send OTP (Step 2)
     */
    sendOTP: async (data) => {
        try {
            // Transform camelCase to snake_case for backend
            const payload = {
                username: data.username,
                email: data.email,
                first_name: data.firstName,
                last_name: data.lastName,
                purpose: 'registration'
            };
            console.log('📤 Sending OTP request:', payload);
            const response = await apiClient.post('/register/send-otp/', payload);
            console.log('✅ Raw Axios Response:', {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers,
                data: response.data
            });
            console.log('✅ OTP API Response Data:', JSON.stringify(response.data, null, 2));
            
            // Return the data directly from backend
            return response.data;
        } catch (error) {
            console.error('❌ OTP API Error:', error);
            console.error('❌ Error Status:', error.response?.status);
            console.error('❌ Error Response:', error.response?.data);
            console.error('❌ Error Message:', error.message);
            throw error;
        }
    },

    /**
     * Verify OTP (Step 3)
     */
    verifyOTP: async (email, otpCode) => {
        const response = await apiClient.post('/register/verify-otp/', {
            email,
            otp_code: otpCode,
            purpose: 'registration'
        });
        return response.data;
    },

    /**
     * Create password and complete registration (Step 4)
     */
    createPassword: async (email, password, confirmPassword) => {
        const response = await apiClient.post('/register/create-password/', {
            email,
            password,
            confirm_password: confirmPassword
        });
        return response.data;
    },

    /**
     * Resend OTP
     */
    resendOTP: async (email) => {
        const response = await apiClient.post('/register/resend-otp/', {
            email,
            purpose: 'registration'
        });
        return response.data;
    },

    /**
     * User login
     */
    userLogin: async (usernameOrEmail, password, rememberMe = false) => {
        const response = await apiClient.post('/login/user/', {
            username_or_email: usernameOrEmail,
            password,
            remember_me: rememberMe
        });
        
        if (response.data.success) {
            // Store tokens
            localStorage.setItem('accessToken', response.data.tokens.access);
            localStorage.setItem('refreshToken', response.data.tokens.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        return response.data;
    },

    /**
     * Admin login
     */
    adminLogin: async (username, password) => {
        const response = await apiClient.post('/login/admin/', {
            username,
            password
        });
        
        if (response.data.success) {
            // Store tokens
            localStorage.setItem('accessToken', response.data.tokens.access);
            localStorage.setItem('refreshToken', response.data.tokens.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        return response.data;
    },

    /**
     * Google OAuth authentication
     */
    googleAuth: async (googleToken) => {
        const response = await apiClient.post('/google/auth/', {
            token: googleToken
        });
        
        if (response.data.success) {
            // Store tokens
            localStorage.setItem('accessToken', response.data.tokens.access);
            localStorage.setItem('refreshToken', response.data.tokens.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        return response.data;
    },

    /**
     * Get Google OAuth config
     */
    getGoogleConfig: async () => {
        const response = await apiClient.get('/google/config/');
        return response.data.config;
    },

    /**
     * Check password strength
     */
    checkPasswordStrength: async (password) => {
        const response = await apiClient.post('/password-strength/', {
            password
        });
        return response.data.data;
    },

    /**
     * Get user profile
     */
    getUserProfile: async () => {
        const response = await apiClient.get('/profile/');
        return response.data.user;
    },

    /**
     * Logout
     */
    logout: async () => {
        const refreshToken = localStorage.getItem('refreshToken');
        
        try {
            await apiClient.post('/logout/', {
                refresh_token: refreshToken
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local storage
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
        }
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('accessToken');
    },

    /**
     * Get current user
     */
    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
};

export default authService;
