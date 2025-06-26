// In website/js/stores/auth.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api-client';

export const useAuthStore = defineStore('auth', () => {
  // STATE
  const user = ref(null);
  const returnUrl = ref(null);
  const router = useRouter();

  // GETTERS
  const isAuthenticated = computed(() => !!user.value);
  const isB2BAuthenticated = computed(() => isAuthenticated.value && user.value.is_b2b);
  const b2bStatus = computed(() => {
      if (isB2BAuthenticated.value && user.value.b2b_account) {
          return user.value.b2b_account.status;
      }
      return null;
  });

  // ACTIONS
  /**
   * Sets a URL to redirect to after a successful login.
   * To be called by a navigation guard before redirecting to a login page.
   * @param {string} url The URL to redirect to.
   */
  function setReturnUrl(url) {
      returnUrl.value = url;
  }

  /**
   * Handles the B2C user login flow.
   * @param {string} email
   * @param {string} password
   */
  async function login(credentials) {
      try {
          const response = await apiClient.login(credentials); // Assumes login method in apiClient
          if (response.mfa_required) {
              // The user needs to complete the MFA step.
              // Redirect to the MFA verification page.
              router.push('/login/verify-mfa');
          } else {
              // MFA not needed or already passed, complete the login.
              user.value = response.user;
              router.push(returnUrl.value || '/account');
              returnUrl.value = null;
          }
      } catch (error) {
          console.error("Login failed:", error);
          // Propagate error to be handled by the component
          throw error;
      }
  }

  async function verifyMfa(token) {
      // This action calls the MFA verification endpoint
      const loggedInUser = await apiClient.verifyMfa({ token });
      user.value = loggedInUser;
      router.push(returnUrl.value || '/account');
      returnUrl.value = null;
  }

  /**
   * Handles the B2B user login flow.
   * @param {object} credentials
   */
  async function loginB2B(credentials) {
      user.value = await apiClient.b2bLogin(credentials);
      router.push(returnUrl.value || '/pro/dashboard');
      returnUrl.value = null;
  }

  /**
   * Logs out the current user, clears state, and redirects.
   */
  async function logout() {
      const wasB2B = isB2BAuthenticated.value;
      try {
          if (wasB2B) {
              await apiClient.b2bLogout();
          } else {
              await apiClient.logout();
          }
      } catch (error) {
          console.error("Logout notification to server failed, but logging out client-side anyway.", error);
      } finally {
          user.value = null;
          router.push(wasB2B ? '/professionnels' : '/');
      }
  }

  /**
   * Checks the backend for an active session to initialize the store.
   */
  async function checkSession() {
      try {
          user.value = await apiClient.checkSession();
      } catch (error) {
          user.value = null;
      }
  }

  return { 
      user, 
      isAuthenticated, 
      isB2BAuthenticated,
      b2bStatus,
      setReturnUrl,
      checkSession, 
      login,
     verifyMfa,
      loginB2B,
      logout,
  };
}, {
  persist: true, // This enables persistence for this store
});
