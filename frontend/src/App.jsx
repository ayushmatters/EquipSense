import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Modern Auth Components
import AuthLogin from './components/auth/Login';
import AuthRegister from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import VerifyResetOTP from './components/auth/VerifyResetOTP';
import ResetPassword from './components/auth/ResetPassword';

// Pages - Lazy load
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const AdminDashboard = React.lazy(() => import('./pages/AdminDashboard'));
const ManageUsers = React.lazy(() => import('./pages/ManageUsers'));
const AdminSettings = React.lazy(() => import('./pages/AdminSettings'));
const UploadPage = React.lazy(() => import('./pages/UploadPage'));
const HistoryPage = React.lazy(() => import('./pages/HistoryPage'));

// Protected Route Components
import AdminProtectedRoute from './components/AdminProtectedRoute';
import UserProtectedRoute from './components/UserProtectedRoute';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <Router>
      <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
        <React.Suspense fallback={<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px' }}>Loading...</div>}>
          <Routes>
            {/* Modern Authentication Routes */}
            <Route path="/login" element={<AuthLogin />} />
            <Route path="/register" element={<AuthRegister />} />
            <Route path="/auth/login" element={<AuthLogin />} />
            <Route path="/auth/register" element={<AuthRegister />} />
            <Route path="/auth/forgot-password" element={<ForgotPassword />} />
            <Route path="/auth/verify-reset-otp" element={<VerifyResetOTP />} />
            <Route path="/auth/reset-password" element={<ResetPassword />} />
            
            {/* User Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <UserProtectedRoute>
                  <Dashboard darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
                </UserProtectedRoute>
              }
            />
            <Route
              path="/upload"
              element={
                <UserProtectedRoute>
                  <UploadPage darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
                </UserProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <UserProtectedRoute>
                  <HistoryPage darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
                </UserProtectedRoute>
              }
            />
            
            {/* Admin Protected Routes */}
            <Route
              path="/admin-dashboard"
              element={
                <AdminProtectedRoute>
                  <AdminDashboard />
                </AdminProtectedRoute>
              }
            />
            <Route
              path="/admin-dashboard/manage-users"
              element={
                <AdminProtectedRoute>
                  <ManageUsers />
                </AdminProtectedRoute>
              }
            />
            <Route
              path="/admin-dashboard/settings"
              element={
                <AdminProtectedRoute>
                  <AdminSettings />
                </AdminProtectedRoute>
              }
            />
            
            {/* Default Route - Redirect to modern auth */}
            
            {/* Default Route - Redirect to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </React.Suspense>
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme={darkMode ? 'dark' : 'light'}
        />
      </div>
    </Router>
  );
}

export default App;

