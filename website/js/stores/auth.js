/**
 * @file /stores/auth.js
 * @description Pinia store for managing authentication state.
 * This store is the single source of truth for the user's authentication token
 * and profile. It replaces the insecure use of localStorage.
 */
import { defineStore } from 'pinia';
import { apiClient } from '@/js/api-client.js';

// Helper to get initial token from a secure cookie if it exists (ideal setup)
// Or returns null if not present. For this example, we start fresh.
const getInitialToken = () => {
  // In a truly secure setup with HttpOnly cookies, you wouldn't need this.
  // The token would be managed by the browser and backend.
  // This store would primarily hold user info and login status.
  return null;
};

export const useAuthStore = defineStore('auth', {
  // STATE: The core data of the store.
  state: () => ({
    accessToken: getInitialToken(),
    user: null,
    isAuthenticated: !!getInitialToken(),
    returnUrl: null, // To store the URL to redirect to after login
  }),

  // GETTERS: Computed properties derived from state.
  getters: {
    /**
     * Provides the current access token.
     * @returns {string | null}
     */
    getToken: (state) => state.accessToken,

    /**
     * Provides the current user's data.
     * @returns {object | null}
     */
    getUser: (state) => state.user,

    /**
     * Checks if the user is authenticated.
     * @returns {boolean}
     */
    isLoggedIn: (state) => !!state.accessToken,
  },

  // ACTIONS: Methods that can mutate the state.
  actions: {
    /**
     * Sets the authentication token in the store.
     * @param {string} token The JWT access token.
     */
    setToken(token) {
      this.accessToken = token;
      this.isAuthenticated = true;
    },

    /**
     * Clears the authentication token and user data from the store.
     */
    clearToken() {
      this.accessToken = null;
      this.user = null;
      this.isAuthenticated = false;
    },

    /**
     * Sets the user profile data.
     * @param {object} userData The user's profile information.
     */
    setUser(userData) {
      this.user = userData;
    },
    
    /**
     * Handles the complete login flow.
     * @param {string} email
     * @param {string} password
     * @returns {Promise<boolean>} True if login is successful.
     */
    async login(email, password) {
      try {
        const response = await apiClient.post('/auth/login', { email, password });
        if (response && response.access_token) {
          this.setToken(response.access_token);
          // Optionally fetch user profile after login
          await this.fetchProfile();
          // Redirect to the stored return URL or a default page
          window.location.href = this.returnUrl || '/compte.html';
          return true;
        }
        // If login is unsuccessful, clear any previous state
        this.logout();
        return false;
      } catch (error) {
        console.error("Login failed:", error);
        this.logout();
        return false;
      }
    },

    /**
     * Handles the complete logout flow.
     */
    async logout() {
      // It's good practice to notify the backend of logout,
      // which allows for server-side token invalidation.
      try {
        await apiClient.post('/auth/logout', {});
      } catch (error) {
        console.error("Logout notification to server failed, but logging out client-side anyway.", error);
      } finally {
        this.clearToken();
        // Redirect to homepage after logout
        window.location.href = '/';
      }
    },
    
    /**
     * Fetches the user's profile from the API and stores it.
     */
    async fetchProfile() {
        if (!this.isLoggedIn) return;
        try {
            const profileData = await apiClient.get('/account/profile');
            if (profileData) {
                this.setUser(profileData.data);
            }
        } catch (error) {
            console.error("Failed to fetch user profile:", error);
            // If the token is invalid (e.g., expired), log the user out
            if (error.response && error.response.status === 401) {
              this.logout();
            }
        }
    },
  },
});
