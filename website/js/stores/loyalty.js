import { defineStore } from 'pinia';
import { apiClient } from '../api-client';
import { useNotificationStore } from './notification';

export const useLoyaltyStore = defineStore('loyalty', {
  state: () => ({
    rewards: [],
    isLoading: false,
  }),
  actions: {
    async fetchExclusiveRewards() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/loyalty/exclusive-rewards');
        this.rewards = response.data;
      } catch (error) {
        console.error("Failed to fetch rewards:", error);
        useNotificationStore().showNotification({
          message: 'Could not load rewards.',
          type: 'error'
        });
      } finally {
        this.isLoading = false;
      }
    },
    async redeemReward(rewardId) {
      const notificationStore = useNotificationStore();
      try {
        await apiClient.post('/loyalty/redeem-reward', { reward_id: rewardId });
        notificationStore.showNotification({
          message: 'Reward redeemed successfully!',
          type: 'success'
        });
        // Optionally, you might want to refresh user points data here
        // For example: useUserStore().fetchUserProfile();
        return true;
      } catch (error) {
        console.error("Failed to redeem reward:", error);
        notificationStore.showNotification({
          message: error.response?.data?.error || 'Redemption failed.',
          type: 'error'
        });
        return false;
      }
    },
  },
});
    return { status, referral, isLoading, fetchLoyaltyData };
});
