import React from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import authService from '../../services/authService';
import { toast } from '../../utils/toast';
import { useNavigate } from 'react-router-dom';
import '../../styles/auth.css';

const GoogleAuthButton = ({ mode = 'signup' }) => {
    const navigate = useNavigate();
    const [config, setConfig] = React.useState(null);

    React.useEffect(() => {
        const fetchConfig = async () => {
            try {
                const googleConfig = await authService.getGoogleConfig();
                setConfig(googleConfig);
            } catch (error) {
                console.error('Failed to fetch Google config:', error);
            }
        };
        fetchConfig();
    }, []);

    const handleGoogleSuccess = async (credentialResponse) => {
        try {
            const response = await authService.googleAuth(credentialResponse.credential);
            
            if (response.success) {
                toast.success(`Welcome ${response.user.first_name}!`);
                
                // Redirect based on user type
                if (response.user.is_admin) {
                    navigate('/admin-dashboard');
                } else {
                    navigate('/dashboard');
                }
            }
        } catch (error) {
            toast.error(error.response?.data?.message || 'Google authentication failed');
        }
    };

    const handleGoogleError = () => {
        toast.error('Google sign-in was unsuccessful. Please try again.');
    };

    if (!config?.client_id) {
        return null;
    }

    return (
        <GoogleOAuthProvider clientId={config.client_id}>
            <div className="google-auth-container">
                <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={handleGoogleError}
                    text={mode === 'signup' ? 'signup_with' : 'signin_with'}
                    shape="rectangular"
                    theme="outline"
                    size="large"
                />
            </div>
        </GoogleOAuthProvider>
    );
};

export default GoogleAuthButton;
