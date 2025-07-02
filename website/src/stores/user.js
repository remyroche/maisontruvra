import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from './notification';
import { useCartStore } from './cart';

/**
 * Manages user state, including authentication, profile information,
 * and account-related actions.
 */
export const useUserStore = defineStore('user', () => {
  // --- STATE ---
  const user = ref(null);
  const isAuthenticated = ref(null); // null: unknown, false: logged out, true: logged in

  // --- GETTERS ---
  const isB2B = computed(() => user.value?.is_b2b === true);

  // --- ACTIONS ---

  /**
   * Checks the backend for the current authentication status.
   * This is the primary way to sync the frontend's auth state with the server.
   */
  async function checkAuthStatus() {
    try {
      const response = await api.get('/auth/status');
      user.value = response.data.user;
      isAuthenticated.value = response.data.is_authenticated;
    } catch (error) {
      user.value = null;
      isAuthenticated.value = false;
    }
  }

  /**
   * Logs in the user with the provided credentials.
   * @param {object} credentials - { email, password }
   * @returns {boolean} - True if login was successful, false otherwise.
   */
  async function login(credentials) {
    const notificationStore = useNotificationStore();
    try {
      await api.post('/auth/login', credentials);
      await checkAuthStatus(); // Refresh user state after successful login
      notificationStore.addNotification('Login successful!', 'success');
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed. Please check your credentials.';
      notificationStore.addNotification(errorMessage, 'error');
      isAuthenticated.value = false;
      return false;
    }
  }

  /**
   * Logs the current user out.
   */
  async function logout() {
    const notificationStore = useNotificationStore();
    try {
      await api.post('/auth/logout');
      user.value = null;
      isAuthenticated.value = false;
      useCartStore().clearCart(); // Clear cart on logout
      notificationStore.addNotification('You have been logged out.', 'success');
    } catch (error) {
      notificationStore.addNotification('Logout failed. Please try again.', 'error');
    }
  }

  /**
   * Registers a new B2C user account.
   * @param {object} userInfo - User registration data.
   * @returns {boolean} - True if registration was successful.
   */
  async function register(userInfo) {
    const notificationStore = useNotificationStore();
    try {
      await api.post('/auth/register', userInfo);
      notificationStore.addNotification('Registration successful! Please log in.', 'success');
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed.';
      notificationStore.addNotification(errorMessage, 'error');
      return false;
    }
  }

  /**
   * Updates the current user's profile information.
   * @param {object} profileData - The data to update.
   * @returns {boolean} - True if update was successful.
   */
  async function updateProfile(profileData) {
    const notificationStore = useNotificationStore();
    try {
      const response = await api.put('/account/profile', profileData);
      user.value = response.data; // Update local profile with the response
      notificationStore.addNotification('Profile updated successfully.', 'success');
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to update profile.';
      notificationStore.addNotification(errorMessage, 'error');
      return false;
    }
  }

  /**
   * Sends a request to soft-delete the user's own account.
   * @returns {boolean} - True if the deletion request was successful.
   */
  async function deleteAccount() {
    const notificationStore = useNotificationStore();
    try {
      const response = await api.delete('/account/delete');
      notificationStore.addNotification(response.data.message, 'success');
      
      // Clear local state after successful deletion
      user.value = null;
      isAuthenticated.value = false;
      useCartStore().clearCart();
      
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to delete account.';
      notificationStore.addNotification(errorMessage, 'error');
      return false;
    }
  }

  // Expose state, getters, and actions
  return {
    user,
    isAuthenticated,
    isB2B,
    checkAuthStatus,
    login,
    logout,
    register,
    updateProfile,
    deleteAccount
  };
});
