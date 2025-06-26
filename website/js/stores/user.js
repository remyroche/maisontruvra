// website/source/js/stores/user.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '../api-client.js';

export const useUserStore = defineStore('user', () => {
  state: () => ({
    user: null,
    mfaSetupData: {
      secret: null,
      qrCode: null,
    },
  }),
  actions: {
    async fetchUser() {
      try {
        const response = await apiClient.get('/api/account/profile');
        this.user = response.data;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        this.user = null;
      }
    },
    async enableMFA() {
      try {
        const response = await apiClient.post('/api/account/mfa/setup');
        const blob = await response.blob();
        this.mfaSetupData.qrCode = URL.createObjectURL(blob);
        // The secret is now handled server-side in the session, but if you needed it:
        // this.mfaSetupData.secret = response.headers.get('X-MFA-Secret');
        return { success: true };
      } catch (error) {
        console.error('Failed to enable MFA:', error);
        return { success: false, error: 'Failed to start MFA setup.' };
      }
    },
    async confirmMFA(totpCode) {
      try {
        const response = await apiClient.post('/api/account/mfa/enable', { totp_code: totpCode });
        if (response.status === 200) {
          this.fetchUser(); // Refresh user data to get updated 2FA status
          this.clearMfaSetup();
          return { success: true };
        }
      } catch (error) {
        console.error('Failed to confirm MFA:', error);
        return { success: false, error: error.response?.data?.error || 'Invalid code.' };
      }
    },
    async disableMFA() {
        try {
            await apiClient.post('/api/account/mfa/disable');
            this.fetchUser(); // Refresh user data
            return { success: true };
        } catch (error) {
            console.error('Failed to disable MFA:', error);
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
  },
});

// STATE
    const profile = ref(null);
    const orders = ref([]);
    const isAuthenticated = ref(false);
    const isLoading = ref(false);

    // ACTIONS
    async function fetchProfile() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/account/profile');
            profile.value = data;
            isAuthenticated.value = true;
        } catch (error) {
            profile.value = null;
            isAuthenticated.value = false;
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchOrders() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/account/orders');
            orders.value = data.orders;
        } catch(error) {
            console.error("Failed to fetch orders:", error);
        } finally {
            isLoading.value = false;
        }
    }
    
    // Add login/logout/register actions similar to the B2B authStore if needed

    return { profile, orders, isAuthenticated, isLoading, fetchProfile, fetchOrders };
});
