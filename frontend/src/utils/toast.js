/**
 * Toast Notification System
 * Simple toast notifications for user feedback
 */

import { toast as reactToastify } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const defaultOptions = {
    position: 'top-right',
    autoClose: 4000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
};

export const toast = {
    success: (message, options = {}) => {
        reactToastify.success(message, { ...defaultOptions, ...options });
    },
    
    error: (message, options = {}) => {
        reactToastify.error(message, { ...defaultOptions, ...options });
    },
    
    info: (message, options = {}) => {
        reactToastify.info(message, { ...defaultOptions, ...options });
    },
    
    warning: (message, options = {}) => {
        reactToastify.warning(message, { ...defaultOptions, ...options });
    },
    
    loading: (message) => {
        return reactToastify.loading(message);
    },
    
    update: (toastId, options) => {
        reactToastify.update(toastId, options);
    },
    
    dismiss: (toastId) => {
        reactToastify.dismiss(toastId);
    }
};

export default toast;
