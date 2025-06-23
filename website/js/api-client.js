/**
 * @file /js/api-client.js
 * @description Centralized client for making API requests.
 * This version integrates with the Pinia auth store to automatically attach
 * the JWT Bearer token to requests. It also continues to handle CSRF tokens.
 */
import { useAuthStore } from './stores/auth.js';
import { useNotificationStore } from './stores/notification.js';

class ApiClient {
    constructor() {
        this.baseUrl = '/api'; // Assumes API is on the same origin
    }

    /**
     * A helper function to get the current auth token from the Pinia store.
     * @returns {string|null} The access token or null if not available.
     */
    _getAuthToken() {
        // We must use the store within a function call, as it might not be
        // initialized when this class is first instantiated.
        try {
            const authStore = useAuthStore();
            return authStore.getToken;
        } catch (error) {
            // Pinia store might not be available yet if this is called outside a component setup context.
            // This is a failsafe.
            return null;
        }
    }

    /**
     * A helper function to read a cookie value by name.
     * This is useful for retrieving the CSRF token if it's set in a cookie.
     * @param {string} name The name of the cookie.
     * @returns {string|null} The value of the cookie or null.
     */
    _getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const notificationStore = useNotificationStore();

        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers,
        };

        // --- JWT Bearer Token Handling (Security Fix) ---
        // Get the token from our secure in-memory store (Pinia).
        const token = this._getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // --- CSRF Token Handling (Best Practice) ---
        // Automatically reads the CSRF token from a standard cookie (e.g., 'XSRF-TOKEN')
        // and sends it back in the 'X-CSRF-Token' header. This is a robust pattern for SPAs.
        const csrfToken = this._getCookie('XSRF-TOKEN');
        if (csrfToken) {
            headers['X-CSRF-Token'] = csrfToken;
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ 
                    message: `Une erreur de réseau est survenue: ${response.statusText}` 
                }));

                notificationStore.showNotification(errorData.message || `Erreur: ${response.statusText}`, 'error');
                
                // Add the response to the error object so it can be inspected by the caller.
                const error = new Error(errorData.message);
                error.response = response;
                throw error;
            }

            // Handle successful but empty responses (e.g., HTTP 204 No Content).
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            // Re-throw the error so that the calling function knows the request failed
            // and can stop its execution (e.g., stop a loading spinner).
            throw error;
        }
    }

    // --- Standard HTTP Method Helpers ---
    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    post(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
    }

    put(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
    }

    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

export const apiClient = new ApiClient();

