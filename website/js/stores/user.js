import { defineStore } from 'pinia';
import { apiClient } from '../api-client';

export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null,
    isLoggedIn: false,
    isLoading: false,
    orders: [],
    referralCode: null,
    mfaSetupData: {
      secret: null,
      qrCode: null,
    },
  }),
  getters: {
    userInitial: (state) => {
      if (state.profile && state.profile.first_name) {
        return state.profile.first_name.charAt(0).toUpperCase();
      }
      return '';
    },
    getReferralCode: (state) => state.referralCode,
  },
  actions: {
    /**
     * Checks the user's authentication status with the backend.
     */
    async checkAuthStatus() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/auth/status');
        if (response.data.is_logged_in) {
          this.isLoggedIn = true;
          this.profile = response.data.user;
        } else {
          this.logout(); // Ensure state is clean on logged-out status
        }
      } catch (error) {
        this.logout();
        console.error("Error checking auth status:", error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetches the full user profile if it's not already loaded.
     */
    async fetchUserProfile() {
      if (this.isLoggedIn && !this.profile) {
        this.isLoading = true;
        try {
          const response = await apiClient.get('/api/account/profile');
          this.profile = response.data;
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          // Potentially handle logout if profile fetch fails for an authenticated user
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    /**
     * Fetches the user's order history.
     */
    async fetchOrders() {
        if (!this.isLoggedIn) return;
        this.isLoading = true;
        try {
            const response = await apiClient.get('/account/orders');
            this.orders = response.data.orders;
        } catch(error) {
            console.error("Failed to fetch orders:", error);
            this.orders = [];
        } finally {
            this.isLoading = false;
        }
    },

    /**
     * Fetches and caches the user's referral code.
     */
    async fetchReferralCode() {
      if (this.isLoggedIn && this.referralCode === null) {
        try {
          const response = await apiClient.get('/b2b/loyalty/referral-code');
          this.referralCode = response.data.referral_code || 'not_found';
        } catch (error) {
          console.error("Error fetching referral code:", error);
          this.referralCode = 'error';
        }
      }
    },

    /**
     * Initiates the MFA setup process.
     */
    async enableMFA() {
      try {
        const response = await apiClient.post('/api/account/mfa/setup', {}, { responseType: 'blob' });
        this.mfaSetupData.qrCode = URL.createObjectURL(response.data);
        return { success: true };
      } catch (error) {
        console.error('Failed to enable MFA:', error);
        return { success: false, error: 'Failed to start MFA setup.' };
      }
    },

    /**
     * Confirms and enables MFA with the provided TOTP code.
     */
    async confirmMFA(totpCode) {
      try {
        await apiClient.post('/api/account/mfa/enable', { totp_code: totpCode });
        this.fetchUserProfile(); // Refresh user data to get updated 2FA status
        this.clearMfaSetup();
        return { success: true };
      } catch (error) {
        console.error('Failed to confirm MFA:', error);
        return { success: false, error: error.response?.data?.error || 'Invalid code.' };
      }
    },
    
    /**
     * Disables MFA for the user.
     */
    async disableMFA() {
        try {
            await apiClient.post('/api/account/mfa/disable');
            this.fetchUserProfile(); // Refresh user data
            return { success: true };
        } catch (error) {
            console.error('Failed to disable MFA:', error);
            return { success: false, error: 'Could not disable 2FA.' };
        }
    },

    /**
     * Clears temporary MFA setup data.
     */
    clearMfaSetup() {
      if (this.mfaSetupData.qrCode) {
        URL.revokeObjectURL(this.mfaSetupData.qrCode);
      }
      this.mfaSetupData.secret = null;
      this.mfaSetupData.qrCode = null;
    },

    /**
     * Clears all user-related state.
     */
    logout() {
      this.isLoggedIn = false;
      this.profile = null;
      this.orders = [];
      this.referralCode = null;
      this.clearMfaSetup();
      // Note: The actual API call to /auth/logout should be handled separately
      // where the logout action is dispatched.
    }
  },
});
