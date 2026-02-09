/**
 * Admin API Service
 * API calls for admin dashboard and user management
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const ADMIN_URL = `${API_BASE_URL}/auth/admin`;

// Create axios instance with auth token
const adminClient = axios.create({
    baseURL: ADMIN_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
adminClient.interceptors.request.use(
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
adminClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

const adminService = {
    /**
     * Get dashboard statistics
     */
    getDashboardStats: async () => {
        const response = await adminClient.get('/dashboard-stats/');
        return response.data;
    },

    /**
     * Get all users
     */
    getAllUsers: async (filters = {}) => {
        const params = new URLSearchParams();
        if (filters.role) params.append('role', filters.role);
        if (filters.search) params.append('search', filters.search);
        
        const response = await adminClient.get(`/users/?${params.toString()}`);
        return response.data;
    },

    /**
     * Delete user
     */
    deleteUser: async (userId) => {
        const response = await adminClient.delete(`/users/${userId}/delete/`);
        return response.data;
    },

    /**
     * Toggle user active status
     */
    toggleUserStatus: async (userId) => {
        const response = await adminClient.patch(`/users/${userId}/toggle-status/`);
        return response.data;
    },

    /**
     * Change user role
     */
    changeUserRole: async (userId, newRole) => {
        const response = await adminClient.patch(`/users/${userId}/change-role/`, {
            role: newRole
        });
        return response.data;
    }
};

export default adminService;
