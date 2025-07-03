// website/src/stores/user.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from './notification';
import { useCartStore } from './cart';

/**
 * Manages user state, including authentication, profile information,
 * and account-related actions like the wishlist.
 */
export const useUserStore = defineStore('user', () => {
  // --- STATE ---
  const user = ref(null);
  const isAuthenticated = ref(null); // null: unknown, false: logged out, true: logged in
  const wishlist = ref([]); // Holds the user's wishlist items

  // --- GETTERS ---
  const isB2B = computed(() => user.value?.is_b2b === true);
  const isProductInWishlist = computed(() => {
    return (productId) => wishlist.value.some(item => item.product_id === productId);
  });

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
      if (isAuthenticated.value) {
        await fetchWishlist(); // Fetch wishlist if user is logged in
      }
    } catch (error) {
      user.value = null;
      isAuthenticated.value = false;
      wishlist.value = []; // Clear wishlist if auth check fails
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
      await checkAuthStatus(); // Refreshes user and wishlist state
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
   * Unified login for both B2B and B2C users.
   * @param {object} credentials - { email, password }
   * @returns {object} - Login response data
   */
  async function loginUnified(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      
      if (!response.data.requires_2fa) {
        // Login successful without 2FA
        user.value = response.data.user;
        isAuthenticated.value = true;
        await fetchWishlist();
      }
      
      return response.data;
    } catch (error) {
      isAuthenticated.value = false;
      throw error;
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
      wishlist.value = []; // Clear wishlist on logout
      useCartStore().clearCart();
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
   * Unified registration for both B2B and B2C users.
   * @param {object} userInfo - User registration data.
   * @returns {object} - Registration response data.
   */
  async function registerUnified(userInfo) {
    try {
      const response = await api.post('/auth/register', userInfo);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Verify 2FA token during login.
   * @param {object} mfaData - { user_id, mfa_token, mfa_type }
   * @returns {object} - Verification response data.
   */
  async function verify2FA(mfaData) {
    try {
      const response = await api.post('/auth/verify-2fa', mfaData);
      
      // Login successful after 2FA
      user.value = response.data.user;
      isAuthenticated.value = true;
      await fetchWishlist();
      
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Setup TOTP for the current user.
   * @returns {object} - TOTP setup data (secret, QR code).
   */
  async function setupTotp() {
    try {
      const response = await api.post('/auth/setup-totp');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Confirm TOTP setup with verification code.
   * @param {string} totpCode - TOTP verification code.
   * @returns {boolean} - True if setup confirmed.
   */
  async function confirmTotpSetup(totpCode) {
    try {
      await api.post('/auth/confirm-totp', { totp_code: totpCode });
      return true;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Request a magic link for authentication.
   * @param {object} linkData - { email }
   * @returns {boolean} - True if request sent.
   */
  async function requestMagicLink(linkData) {
    try {
      await api.post('/auth/request-magic-link', linkData);
      return true;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Update authentication methods (enable/disable TOTP or magic link).
   * @param {object} updateData - Authentication method update data.
   * @returns {boolean} - True if update successful.
   */
  async function updateAuthMethod(updateData) {
    try {
      await api.post('/auth/update-auth-method', updateData);
      return true;
    } catch (error) {
      throw error;
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
      user.value = response.data;
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
      wishlist.value = [];
      useCartStore().clearCart();
      
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to delete account.';
      notificationStore.addNotification(errorMessage, 'error');
      return false;
    }
  }

  // --- WISHLIST ACTIONS ---

  async function fetchWishlist() {
    if (!isAuthenticated.value) return;
    try {
      const response = await api.get('/api/wishlist');
      wishlist.value = response.data;
    } catch (err) {
      useNotificationStore().addNotification('Could not load wishlist.', 'error');
    }
  }

  async function addToWishlist(productId) {
    if (!isAuthenticated.value) return;
    try {
      const response = await api.post('/api/wishlist/items', { product_id: productId });
      wishlist.value.push(response.data);
      useNotificationStore().addNotification('Added to wishlist!', 'success');
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to add to wishlist.';
      useNotificationStore().addNotification(errorMessage, 'error');
      throw err;
    }
  }

  async function removeFromWishlist(productId) {
    if (!isAuthenticated.value) return;
    try {
        // We need the wishlist *item* ID to delete, not the product ID.
        const item = wishlist.value.find(i => i.product_id === productId);
        if (!item) return;

        await api.delete(`/api/wishlist/items/${item.id}`);
        wishlist.value = wishlist.value.filter(i => i.product_id !== productId);
        useNotificationStore().addNotification('Removed from wishlist.', 'success');
    } catch (err) {
        const errorMessage = err.response?.data?.error || 'Failed to remove from wishlist.';
        useNotificationStore().addNotification(errorMessage, 'error');
        throw err;
    }
  }

  // Expose state, getters, and actions
  return {
    user,
    isAuthenticated,
    wishlist,
    isB2B,
    isProductInWishlist,
    checkAuthStatus,
    login,
    loginUnified,
    logout,
    register,
    registerUnified,
    verify2FA,
    setupTotp,
    confirmTotpSetup,
    requestMagicLink,
    updateAuthMethod,
    updateProfile,
    deleteAccount,
    fetchWishlist,
    addToWishlist,
    removeFromWishlist,
  };
});
