/**
 * @file /js/auth_service.js
 * @description Manages user authentication API calls and orchestrates state
 * updates via the Pinia store. It is now stateless and does not
 * store tokens directly.
 */
import { useAuthStore } from './stores/auth.js';
import { apiClient } from './api-client.js';

class AuthService {
  /**
   * Attempts to log in a user by calling the auth store's login action.
   * @param {string} email - The user's email.
   * @param {string} password - The user's password.
   * @returns {Promise<boolean>} - True on successful login, false otherwise.
   */
  async login(email, password) {
    const authStore = useAuthStore();
    return authStore.login(email, password);
  }

  /**
   * Logs the current user out by calling the auth store's logout action.
   */
  logout() {
    const authStore = useAuthStore();
    authStore.logout();
  }

  /**
   * Checks if a user is currently authenticated by checking the store.
   * @returns {boolean}
   */
  isLoggedIn() {
    const authStore = useAuthStore();
    return authStore.isLoggedIn;
  }

  /**
   * Registers a new B2C user via the API client.
   * This does not automatically log the user in.
   * @param {object} userData - Object containing user details {name, email, password}.
   * @returns {Promise<any>} - The response data from the API.
   */
  register(userData) {
    // The component handling the registration should decide what to do
    // after a successful registration (e.g., show a message, or log the user in).
    return apiClient.post('/auth/register', userData);
  }
}

export const authService = new AuthService();
