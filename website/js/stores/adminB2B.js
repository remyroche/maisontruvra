import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminB2BStore = defineStore('adminB2B', {
  state: () => ({
    accounts: [],
    account: null, // For single account details
    isLoading: false,
    error: null,
    statuses: ['pending', 'approved', 'rejected'],
  }),
  actions: {
    async fetchB2BAccounts(filters = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/b2b/accounts', { params: filters });
        this.accounts = response.data;
      } catch (error) {
        this.error = 'Failed to fetch B2B accounts.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async approveB2BAccount(accountId) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.put(`/b2b/accounts/${accountId}/approve`);
        await this.fetchB2BAccounts(); // Refresh list
      } catch (error) {
        this.error = 'Failed to approve B2B account.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async updateB2BAccount(accountId, data) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.put(`/b2b/accounts/${accountId}`, data);
            await this.fetchB2BAccounts(); // Refresh list
        } catch (error) {
            this.error = 'Failed to update B2B account.';
            console.error(this.error, error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    },

    async deleteB2BAccount(accountId) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.delete(`/b2b/accounts/${accountId}`);
            await this.fetchB2BAccounts();
        } catch (error) {
            this.error = 'Failed to delete B2B account.';
            console.error(this.error, error);
        } finally {
            this.isLoading = false;
        }
    },
  },
});
