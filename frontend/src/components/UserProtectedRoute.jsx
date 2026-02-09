import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

const UserProtectedRoute = ({ children }) => {
    const isAuthenticated = authService.isAuthenticated();
    const user = authService.getCurrentUser();

    if (!isAuthenticated) {
        return <Navigate to="/auth/login" replace />;
    }

    // Check if user is an admin - redirect to admin dashboard
    const isAdmin = user?.is_staff || user?.is_superuser || user?.is_admin_user || user?.role === 'admin';
    
    if (isAdmin) {
        return <Navigate to="/admin-dashboard" replace />;
    }

    return children;
};

export default UserProtectedRoute;
