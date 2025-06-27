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
    async checkAuthStatus() {
      this.isLoading = true;
      try {
        // Correct Path: No leading '/api'
        const response = await apiClient.get('/auth/status');
        const responseData = response.data.data || response.data;
        
        if (responseData.is_logged_in) {
          this.isLoggedIn = true;
          this.profile = responseData.user;
        } else {
          this.logout();
        }
      } catch (error) {
        this.logout();
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserProfile() {
      if (this.isLoggedIn && !this.profile) {
        this.isLoading = true;
        try {
          // Correct Path: No leading '/api'
          const response = await apiClient.get('/account/profile');
          this.profile = response.data.data || response.data;
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    async fetchOrders() {
        if (!this.isLoggedIn) return;
        this.isLoading = true;
        try {
            // Correct Path: No leading '/api'
            const response = await apiClient.get('/account/orders');
            const responseData = response.data.data || response.data;
            this.orders = responseData.orders;
        } catch(error) {
            console.error("Failed to fetch orders:", error);
            this.orders = [];
        } finally {
            this.isLoading = false;
        }
    },

    async fetchReferralCode() {
      if (this.isLoggedIn && this.referralCode === null) {
        try {
          // Correct Path: No leading '/api'
          const response = await apiClient.get('/b2b/loyalty/referral-code');
          const responseData = response.data.data || response.data;
          this.referralCode = responseData.referral_code || 'not_found';
        } catch (error) {
          console.error("Error fetching referral code:", error);
          this.referralCode = 'error';
        }
      }
    },

    async enableMFA() {
      try {
        // Correct Path: No leading '/api'
        const response = await apiClient.post('/account/mfa/setup', {}, { responseType: 'blob' });
        this.mfaSetupData.qrCode = URL.createObjectURL(response.data);
        return { success: true };
      } catch (error) {
        return { success: false, error: 'Failed to start MFA setup.' };
      }
    },

    async confirmMFA(totpCode) {
      try {
        // Correct Path: No leading '/api'
        await apiClient.post('/account/mfa/enable', { totp_code: totpCode });
        this.fetchUserProfile();
        this.clearMfaSetup();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.response?.data?.error || 'Invalid code.' };
      }
    },
    
    async disableMFA() {
        try {
            // Correct Path: No leading '/api'
            await apiClient.post('/account/mfa/disable');
            this.fetchUserProfile();
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Could not disable 2FA.' };
        }
    },

    clearMfaSetup() {
      if (this.mfaSetupData.qrCode) {
        URL.revokeObjectURL(this.mfaSetupData.qrCode);
      }
      this.mfaSetupData.secret = null;
      this.mfaSetupData.qrCode = null;
    },

    logout() {
      this.isLoggedIn = false;
      this.profile = null;
      this.orders = [];
      this.referralCode = null;
      this.clearMfaSetup();
    }
  },
});
