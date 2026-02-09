import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

const AdminProtectedRoute = ({ children }) => {
    const isAuthenticated = authService.isAuthenticated();
    const user = authService.getCurrentUser();

    if (!isAuthenticated) {
        return <Navigate to="/auth/login" replace />;
    }

    // Check if user has admin role
    const isAdmin = user?.is_staff || user?.is_admin_user || user?.role === 'admin';

    if (!isAdmin) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};

export default AdminProtectedRoute;
