/*
 * FILENAME: website/js/stores/adminAuth.js
 * DESCRIPTION: Pinia store for managing Admin Portal authentication state.
 *
 * This store is the single source of truth for the current admin's session,
 * user details, and permissions. It includes actions for checking authentication
 * status and logging out.
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminAuthStore = defineStore('adminAuth', () => {
  // --- STATE ---
  const adminUser = ref(null); // Holds user object { email, first_name, etc. }
  const permissions = ref([]); // Holds a list of user permissions [ 'manage_users', ... ]
  const error = ref(null); // Holds the last authentication error
  const isLoading = ref(true); // Tracks if we are currently fetching auth status

  // --- GETTERS ---
  const isAuthenticated = computed(() => !!adminUser.value);

  // --- ACTIONS ---

  /**
   * Checks the backend to see if a valid admin session exists.
   * This is called when the app loads to initialize the auth state.
   */
  async function checkAuthStatus() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.get('/auth/status');
      if (response.data.is_authenticated) {
        adminUser.value = response.data.user;
        permissions.value = response.data.permissions;
      } else {
        adminUser.value = null;
        permissions.value = [];
      }
    } catch (err) {
      console.error("Error checking auth status:", err);
      error.value = 'Could not verify session. Please try logging in again.';
      adminUser.value = null;
      permissions.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Logs out the current admin user.
   * This calls the backend logout endpoint and clears the local state.
   */
  async function logout() {
    isLoading.value = true;
    error.value = null;
    try {
      await adminApiClient.post('/auth/logout');
      // Backend call successful, now clear local state
      adminUser.value = null;
      permissions.value = [];
      // --- LOGGING ---
      // The backend's /auth/logout endpoint should be responsible for
      // creating an audit log entry for the successful logout event.
    } catch (err) {
      console.error("Logout failed:", err);
      error.value = 'Logout failed. Please try again.';
      // Even if the API call fails, we clear the frontend state for security.
      adminUser.value = null;
      permissions.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  return {
    adminUser,
    permissions,
    error,
    isLoading,
    isAuthenticated,
    checkAuthStatus,
    logout,
  };
});
