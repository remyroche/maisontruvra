// website/source/js/auth_service.js
import { apiClient } from './api-client.js';

/**
 * Manages B2C user authentication state and actions.
 */
class AuthService {
    /**
     * Attempts to log in a user and stores the token on success.
     * @param {string} email - The user's email.
     * @param {string} password - The user's password.
     * @returns {Promise<boolean>} - True on successful login, false otherwise.
     */
    async login(email, password) {
        try {
            const data = await apiClient.post('/auth/login', { email, password });
            if (data && data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                // Redirect to the account page upon successful login
                window.location.href = '/compte.html';
                return true;
            }
            return false;
        } catch (error) {
            console.error("Login attempt failed:", error);
            // The apiClient already shows a UI notification, so we just return false
            return false;
        }
    }

    /**
     * Logs the current user out by clearing the token and redirecting.
     */
    logout() {
        localStorage.removeItem('access_token');
        // It's good practice to notify the backend if you use token blacklisting
        // apiClient.post('/auth/logout', {}); 
        window.location.href = '/'; // Redirect to the homepage
    }

    /**
     * Checks if a user is currently authenticated.
     * @returns {boolean}
     */
    isLoggedIn() {
        return !!localStorage.getItem('access_token');
    }

    /**
     * Registers a new B2C user.
     * @param {object} userData - Object containing user details {name, email, password}.
     * @returns {Promise<any>} - The response data from the API.
     */
    register(userData) {
        return apiClient.post('/auth/register', userData);
    }
}

export const authService = new AuthService();
