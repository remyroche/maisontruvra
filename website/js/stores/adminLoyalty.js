import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminLoyaltyStore = defineStore('adminLoyalty', {
  state: () => ({
    tiers: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchTiers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/loyalty/tiers');
        this.tiers = response.data;
      } catch (e) {
        this.error = 'Failed to fetch loyalty tiers.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async createTier(tierData) {
      try {
        await apiClient.post('/loyalty/tiers', tierData);
        await this.fetchTiers();
      } catch (e) {
        this.error = 'Failed to create tier.';
        console.error(this.error, e);
        throw e;
      }
    },
    async updateTier(id, tierData) {
      try {
        await apiClient.put(`/loyalty/tiers/${id}`, tierData);
        await this.fetchTiers();
      } catch (e) {
        this.error = 'Failed to update tier.';
        console.error(this.error, e);
        throw e;
      }
    },
    async deleteTier(id) {
      try {
        await apiClient.delete(`/loyalty/tiers/${id}`);
        await this.fetchTiers();
      } catch (e) {
        this.error = 'Failed to delete tier.';
        console.error(this.error, e);
      }
    },
  },
});
