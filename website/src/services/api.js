/**
 * @file /src/services/api.js
 * @description Centralized API client service.
 * Handles request setup, CSRF token management, and standardized error handling
 * for both public and admin clients.
 */
import axios from 'axios';
import { useNotificationStore } from '@/stores/notification';
import { useAdminAuthStore } from '@/stores/adminAuth';

const createApiClient = (baseURL, isAdmin = false) => {
    const instance = axios.create({
        baseURL,
        withCredentials: true,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    });

    // Response interceptor for centralized error handling and data unwrapping.
    instance.interceptors.response.use(
        response => response.data, // Return data directly on success
        error => {
            const notificationStore = useNotificationStore();
            let message = 'An unexpected error occurred. Please try again later.';

            if (error.response) {
                const { status, data } = error.response;
                message = data?.msg || data?.error || `Error: ${status}`;

                // Handle session timeout for admin users
                if (isAdmin && status === 401 && data?.reason === 'reauth_required') {
                    const adminAuthStore = useAdminAuthStore();
                    adminAuthStore.promptForReAuth(error.config);
                    // Don't show a generic error toast for re-auth prompts
                    return Promise.reject(error);
                }

            } else if (error.request) {
                message = 'Cannot connect to the server. Please check your network connection.';
            } else {
                message = error.message;
            }

            notificationStore.showNotification({ message, type: 'error' });

            return Promise.reject(error);
        }
    );

    // Request interceptor to attach the CSRF token to all state-changing requests.
    instance.interceptors.request.use(async (config) => {
        const methodsWithCsrf = ['post', 'put', 'delete', 'patch'];
        if (methodsWithCsrf.includes(config.method.toLowerCase())) {
            try {
                // Fetch a fresh CSRF token for each state-changing request to ensure validity.
                const { data } = await axios.get('/api/auth/csrf-token', { withCredentials: true });
                if (data.csrf_token) {
                    config.headers['X-CSRF-TOKEN'] = data.csrf_token;
                }
            } catch (e) {
                console.error('Could not fetch CSRF token. Request will likely fail.', e);
                const notificationStore = useNotificationStore();
                notificationStore.showNotification({ message: 'A security error occurred. Please refresh the page.', type: 'error' });
                return Promise.reject(new Error('CSRF Token not available.'));
            }
        }
        return config;
    }, (error) => Promise.reject(error));

    return instance;
};

// Client for the public-facing site
export const apiClient = createApiClient('/api');

// Client for the admin panel with a specific base URL
export const adminApiClient = createApiClient('/api/admin', true);