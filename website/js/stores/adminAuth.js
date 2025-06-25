import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';
import router from '@/js/admin/router';

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    // State for re-authentication flow
    isReAuthRequired: false,
    failedRequest: null,
  }),
  actions: {
    async login(credentials) {
      this.isLoading = true;
      try {
        await apiClient.post('/auth/login', credentials);
        await this.checkAuth();
        if (this.isAuthenticated) {
            router.push({ name: 'AdminDashboard' });
        }
      } catch (error) {
        this.error = 'Login failed. Please check your credentials.';
        this.isAuthenticated = false;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    async logout() {
        try {
            await apiClient.post('/auth/logout');
        } catch (e) {
            console.error("Logout failed, clearing session locally.", e);
        } finally {
            this.user = null;
            this.isAuthenticated = false;
            this.isReAuthRequired = false;
            router.push({ name: 'AdminLogin' });
        }
    },
    
    async checkAuth() {
        this.isLoading = true;
        try {
            const response = await apiClient.get('/auth/status');
            this.user = response.data.user;
            this.isAuthenticated = response.data.is_authenticated;
        } catch (error) {
            this.user = null;
            this.isAuthenticated = false;
        } finally {
            this.isLoading = false;
        }
    },

    promptForReAuth(requestConfig) {
        if (!this.isReAuthRequired) { // Prevent multiple prompts
            this.failedRequest = requestConfig;
            this.isReAuthRequired = true;
        }
    },

    async reauthenticateAndRetry(password) {
        try {
            await apiClient.post('/auth/reauthenticate', { password });
            this.isReAuthRequired = false;
            if (this.failedRequest) {
                const requestToRetry = { ...this.failedRequest };
                this.failedRequest = null;
                return apiClient(requestToRetry);
            }
        } catch (error) {
            console.error("Re-authentication failed", error);
            throw error;
        }
    },
    
    cancelReAuth() {
        this.isReAuthRequired = false;
        this.failedRequest = null;
        this.logout(); // If they cancel, log them out completely.
    }
  },
});
