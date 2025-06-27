import { defineStore } from 'pinia';
import { apiClient } from '../common/adminApiClient';

export const useAdminLoyaltyStore = defineStore('adminLoyalty', {
  state: () => ({
    tiers: [],
    referralTiers: [],
    isLoading: false,
  }),
  actions: {
    async fetchLoyaltyTiers() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/loyalty/tiers');
        this.tiers = response.data;
      } catch (error) {
        console.error("Failed to fetch loyalty tiers:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async createTier(tierData) {
        await apiClient.post('/loyalty/tiers', tierData);
        await this.fetchLoyaltyTiers();
    },
    async updateTier(tierId, tierData) {
        await apiClient.put(`/loyalty/tiers/${tierId}`, tierData);
        await this.fetchLoyaltyTiers();
    },
    async deleteTier(tierId) {
        await apiClient.delete(`/loyalty/tiers/${tierId}`);
        await this.fetchLoyaltyTiers();
    },
    
    // Actions for Referral Reward Tiers
    async fetchReferralTiers() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/loyalty/referral-rewards');
        this.referralTiers = response.data;
      } catch (error) {
        console.error("Failed to fetch referral tiers:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async createReferralTier(tierData) {
        await apiClient.post('/loyalty/referral-rewards', tierData);
        await this.fetchReferralTiers();
    },
    async deleteReferralTier(tierId) {
        await apiClient.delete(`/loyalty/referral-rewards/${tierId}`);
        await this.fetchReferralTiers();
    },
  },
});
