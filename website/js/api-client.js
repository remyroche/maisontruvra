/**
 * @fileoverview
 * API client for interacting with the backend.
 * It handles request setup, CSRF token management, and standardized error handling
 * using Axios interceptors.
 */

import axios from 'axios';
import { useNotificationStore } from '@/stores/notification';

export const apiClient = axios.create({
    baseURL: '/api',
    withCredentials: true, // Necessary for sending HttpOnly cookies
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
});

/**
 * Fetches the CSRF token from a dedicated endpoint.
 * This is called automatically by the request interceptor when needed.
 * @returns {Promise<string|null>} A promise that resolves with the CSRF token, or null on failure.
 */
const getCsrfToken = async () => {
    try {
        const response = await apiClient.get('/auth/csrf-token');
        return response.data.csrf_token;
    } catch (error) {
        console.error('Could not fetch CSRF token:', error);
        const notificationStore = useNotificationStore();
        notificationStore.showNotification("A security error occurred. Please refresh the page and try again.", "error");
        return null;
    }
};

// Use a request interceptor to attach the CSRF token to all state-changing requests.
apiClient.interceptors.request.use(async (config) => {
    const methodsWithCsrf = ['post', 'put', 'delete', 'patch'];
    if (methodsWithCsrf.includes(config.method.toLowerCase())) {
        // No need to check for existing header, the interceptor manages it.
        const csrfToken = await getCsrfToken();
        if (csrfToken) {
            config.headers['X-CSRF-TOKEN'] = csrfToken;
        } else {
            // If we can't get a CSRF token, we should cancel the request.
            return Promise.reject(new Error('CSRF Token not available. Request cancelled.'));
        }
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});


// Use a response interceptor for centralized error handling.
apiClient.interceptors.response.use(
  response => response,
  error => {
    const notificationStore = useNotificationStore();
    
    // Default message
    let message = 'An unexpected error occurred. Please try again later.';

    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        message = error.response.data?.msg || error.response.data?.error || `Error: ${error.response.status}`;
        
        if (error.response.status === 401) {
            // For unauthorized errors, you might want to trigger a logout or redirect to the login page.
            // For now, we just log a more specific error.
            console.error('Authentication error:', message);
            // Example: authStore.logout(); window.location.href = '/login';
        }
    } else if (error.request) {
        // The request was made but no response was received
        message = 'Cannot connect to the server. Please check your network connection.';
        console.error('Network Error:', error.request);
    } else {
        // Something happened in setting up the request that triggered an Error
        message = error.message;
        console.error('Axios Config Error:', message);
    }

    notificationStore.showNotification(message, 'error');

    return Promise.reject(error);
  }
);
