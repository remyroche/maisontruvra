import { defineStore } from 'pinia';
import { adminApiClient } from '@/services/api';
import router from '@/router';

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    isReAuthRequired: false,
    failedRequest: null,
  }),
  actions: {
    async login(credentials) {
      this.isLoading = true;
      try {
        await adminApiClient.post('/auth/login', credentials);
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
            await adminApiClient.post('/auth/logout');
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
            const data = await adminApiClient.get('/auth/status');
            this.user = data.user;
            this.isAuthenticated = data.is_authenticated;
        } catch (error) {
            this.user = null;
            this.isAuthenticated = false;
        } finally {
            this.isLoading = false;
        }
    },

    promptForReAuth(requestConfig) {
        if (!this.isReAuthRequired) {
            this.failedRequest = requestConfig;
            this.isReAuthRequired = true;
        }
    },

    async reauthenticateAndRetry(password) {
        await adminApiClient.post('/auth/reauthenticate', { password });
        this.isReAuthRequired = false;
        const requestToRetry = this.failedRequest;
        this.failedRequest = null;
        if (requestToRetry) {
            return adminApiClient(requestToRetry);
        }
    },
  },
});