/**
 * @file /js/stores/auth.js
 * @description Pinia store for managing authentication state and user profile.
 * This store is the single source of truth for the user's session and data.
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '../api-client';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  // STATE
  const user = ref(null);
  const router = useRouter();

  // GETTERS
  /**
   * Checks if a user is currently authenticated by checking for the user object.
   * @returns {boolean}
   */
  const isAuthenticated = computed(() => !!user.value);

  /**
   * Checks if the authenticated user has a B2B role.
   * @returns {boolean}
   */
  const isB2BAuthenticated = computed(() => {
    return isAuthenticated.value && user.value.is_b2b;
  });
  
  /**
   * Returns the status of the B2B account (e.g., 'approved', 'pending').
   * @returns {string|null}
   */
  const b2bStatus = computed(() => {
    if (isB2BAuthenticated.value && user.value.b2b_account) {
      return user.value.b2b_account.status;
    }
    return null;
  });

  // ACTIONS
  /**
   * Checks the backend for an active session on application startup.
   */
  async function checkSession() {
    try {
      const sessionUser = await apiClient.checkSession();
      user.value = sessionUser;
    } catch (error) {
      user.value = null;
    }
  }

  /**
   * Handles the B2C user login flow.
   * @param {string} email
   * @param {string} password
   */
  async function login(email, password) {
    const loggedInUser = await apiClient.login(email, password);
    user.value = loggedInUser;
  }
  
  /**
   * Handles the B2B user login flow.
   * @param {object} credentials
   */
  async function loginB2B(credentials) {
    const loggedInUser = await apiClient.b2bLogin(credentials);
    user.value = loggedInUser;
  }

  /**
   * Logs out any type of user, clears local state, and redirects.
   */
  async function logout() {
    try {
        if(isB2BAuthenticated.value) {
            await apiClient.b2bLogout();
        } else {
            await apiClient.logout();
        }
    } catch (error) {
        console.error("Logout notification to server failed, but logging out client-side anyway.", error);
    } finally {
        user.value = null;
        // Redirect to the appropriate home/login page
        if(isB2BAuthenticated) {
             router.push('/professionnels');
        } else {
             router.push('/');
        }
    }
  }

  return { 
    user, 
    isAuthenticated, 
    isB2BAuthenticated,
    b2bStatus,
    checkSession, 
    login,
    loginB2B,
    logout,
  };
});
