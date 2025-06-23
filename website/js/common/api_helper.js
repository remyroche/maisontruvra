/**
 * @file website/source/js/common/api_helper.js
 * @description A universal helper for making API requests using fetch.
 * This module centralizes API call logic, including authentication (JWT) and CSRF token headers.
 */

import { getSession } from '../session.js';
import { showToast } from './ui.js'; // Assuming a UI function to show notifications

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Performs a fetch request to the API.
 * This is a private helper function.
 * @param {string} endpoint - The API endpoint to call (e.g., '/users').
 * @param {string} method - The HTTP method (GET, POST, PUT, DELETE).
 * @param {object} [body=null] - The request body for POST/PUT requests.
 * @returns {Promise<object>} - The JSON response from the API.
 */
async function request(endpoint, method, body = null) {
    const session = getSession();
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add JWT token to headers if it exists
    if (session && session.accessToken) {
        headers['Authorization'] = `Bearer ${session.accessToken}`;
    }

    const config = {
        method: method,
        headers: headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        // Auto-refresh token if 401 Unauthorized is received
        // Note: This logic might need to be more sophisticated depending on the auth flow
        if (response.status === 401) {
            console.warn("Received 401, token may have expired.");
            // Optionally, redirect to login or attempt a token refresh
            // window.location.href = '/login.html';
            showToast('Your session has expired. Please log in again.', 'error');
            return { error: "Unauthorized" };
        }

        const data = await response.json();

        if (!response.ok) {
            // Log the error and show a user-friendly message
            console.error(`API Error: ${response.statusText}`, data);
            const errorMessage = data.message || `An error occurred (${response.status})`;
            showToast(errorMessage, 'error');
            return { error: errorMessage, status: response.status };
        }

        return data;

    } catch (error) {
        console.error('Network or other error:', error);
        showToast('A network error occurred. Please try again later.', 'error');
        return { error: 'Network error' };
    }
}

/**
 * A centralized API helper object for making requests to the backend.
 */
export const apiHelper = {
    /**
     * Performs a GET request.
     * @param {string} endpoint - The API endpoint.
     * @returns {Promise<object>}
     */
    get: (endpoint) => request(endpoint, 'GET'),

    /**
     * Performs a POST request.
     * @param {string} endpoint - The API endpoint.
     * @param {object} body - The request body.
     * @returns {Promise<object>}
     */
    post: (endpoint, body) => request(endpoint, 'POST', body),

    /**
     * Performs a PUT request.
     * @param {string} endpoint - The API endpoint.
     * @param {object} body - The request body.
     * @returns {Promise<object>}
     */
    put: (endpoint, body) => request(endpoint, 'PUT', body),

    /**
     * Performs a DELETE request.
     * @param {string} endpoint - The API endpoint.
     * @returns {Promise<object>}
     */
    delete: (endpoint) => request(endpoint, 'DELETE'),
};

async function fetchAPI(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    // Add JWT token to headers if it exists
    const token = localStorage.getItem('jwt_token');
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);

        // Check if the request was successful
        if (!response.ok) {
            let errorData;
            try {
                // Try to parse a JSON error response from the server
                errorData = await response.json();
            } catch (e) {
                // If the response is not JSON, use the status text
                errorData = { error: response.statusText };
            }
            // Throw an error that includes the status and server message
            const error = new Error(errorData.error || `HTTP error! status: ${response.status}`);
            error.status = response.status;
            error.data = errorData;
            throw error;
        }

        // If the response is OK, try to parse it as JSON
        // Handle cases with no content (e.g., 204 No Content)
        if (response.status === 204) {
            return null;
        }
        return await response.json();

    } catch (error) {
        // This catch block handles network errors (e.g., failed to fetch)
        // and the errors thrown from the !response.ok check above.
        console.error('API Fetch Error:', error);

        // Re-throw the error so the calling function can handle it,
        // for example, to show a specific UI message.
        throw error;
    }
}

// A simple helper to get a cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// --- Main API Helper Function ---
async function api(endpoint, { method = 'GET', body = null, headers = {} } = {}) {
    const apiBase = '/api'; // Or load from a config
    const url = `${apiBase}${endpoint}`;

    const defaultHeaders = {
        'Content-Type': 'application/json',
        // Add other default headers if needed
    };

    const token = localStorage.getItem('access_token');
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    // --- FIX: Add CSRF Token to non-GET requests ---
    const csrfToken = getCookie('csrf_token');
    if (csrfToken && method.toUpperCase() !== 'GET') {
        defaultHeaders['X-CSRF-TOKEN'] = csrfToken;
    }
    // --- End of Fix ---

    const config = {
        method,
        headers: {
            ...defaultHeaders,
            ...headers,
        },
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, config);

        if (response.status === 401) {
            // Handle unauthorized access, e.g., redirect to login
            console.error("Unauthorized access. Redirecting to login.");
            // window.location.href = '/login.html'; // Or your admin login page
            return Promise.reject(new Error("Unauthorized"));
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'An unknown error occurred.' }));
            throw new Error(errorData.msg || errorData.message || `HTTP error! status: ${response.status}`);
        }

        // Handle responses that might not have a body (e.g., 204 No Content)
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            return; // Return nothing for non-json responses
        }

    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

export default api;


/**
 * A centralized helper class for making API requests.
 * It automatically handles fetching and attaching JWT and CSRF tokens.
 */
export class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.csrfToken = null;
        // A promise to ensure we don't make requests before the token is fetched.
        this.csrfPromise = null;
    }

    /**
     * Initializes the ApiHelper by fetching the CSRF token.
     * This method should be called once when the application loads.
     * It prevents multiple token requests from being sent simultaneously.
     */
    init() {
        if (!this.csrfPromise) {
            this.csrfPromise = this.fetchCsrfToken().catch(error => {
                console.error("Failed to initialize CSRF token. Subsequent requests may fail.", error);
                // In a production environment, you might want to show a global error message to the user.
                this.csrfPromise = null; // Allow retries on subsequent actions.
            });
        }
        return this.csrfPromise;
    }

    /**
     * Fetches the CSRF token from the backend and stores it in the instance.
     * @private
     */
    async fetchCsrfToken() {
        try {
            // Use a direct fetch call here to avoid a circular dependency on the `request` method itself.
            const response = await fetch(`${this.baseUrl}/auth/csrf-token`);
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            const data = await response.json();
            if (!data.csrf_token) {
                throw new Error("CSRF token not found in the response from the server.");
            }
            this.csrfToken = data.csrf_token;
            console.log('CSRF Token has been successfully fetched and stored for the session.');
        } catch (error) {
            console.error('Critical CSRF Token fetch failed:', error);
            throw error; // Re-throw to be caught by the init() promise.
        }
    }

    setupSecurityHeaders() {
        // Set up default security headers
        this.defaultHeaders = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        };
    }

    sanitizeInput(data) {
        if (typeof data === 'string') {
            return data.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
        }
        return data;
    }

    /**
     * Make a request to the API.
     * @param {string} endpoint - The API endpoint to call (e.g., '/users/1').
     * @param {object} options - The options object for the native fetch call.
     * @returns {Promise<Response>} - A promise that resolves with the raw fetch Response object.
     */
    async request(endpoint, options = {}) {
        const method = options.method || 'GET';

        // For any method that is not a simple GET, ensure the CSRF token has been fetched first.
        if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
            await this.init(); // This will wait for the csrfPromise to resolve.
        }

        const url = `${this.baseUrl}${endpoint}`;

        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers,
        };

        // Automatically add the CSRF token to headers for state-changing methods.
        if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
            if (!this.csrfToken) {
                const errorMessage = 'CSRF token is not available. The request cannot be sent securely.';
                console.error(errorMessage);
                throw new Error(errorMessage);
            }
            headers['X-CSRF-TOKEN'] = this.csrfToken;
        }

        // Add JWT authorization token if it exists in localStorage for either public or admin sessions.
        const token = localStorage.getItem('token') || localStorage.getItem('admin_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers,
        };

        return fetch(url, config);
    }

    /**
     * A wrapper around the request method that handles JSON parsing and error formatting.
     * @param {string} endpoint - The API endpoint.
     * @param {object} options - The fetch options.
     * @returns {Promise<any>} - A promise that resolves with the parsed JSON data.
     */
    async _fetchJson(endpoint, options = {}) {
        try {
            const response = await this.request(endpoint, options);

            if (response.status === 204) { // No Content success status
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = data.message || data.msg || `HTTP error! Status: ${response.status}`;
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            console.error(`API error on ${options.method || 'GET'} ${endpoint}:`, error);
            throw error; // Re-throw so the calling function can handle it.
        }
    }

    // Convenience methods for different HTTP verbs that return parsed JSON
    get(endpoint, options = {}) {
        return this._fetchJson(endpoint, { ...options, method: 'GET' });
    }

    post(endpoint, body, options = {}) {
        return this._fetchJson(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
    }

    put(endpoint, body, options = {}) {
        return this._fetchJson(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
    }

    delete(endpoint, options = {}) {
        return this._fetchJson(endpoint, { ...options, method: 'DELETE' });
    }
}