import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '@/services/api';
import { useNotificationStore } from './notification';

export const useLoyaltyStore = defineStore('loyalty', () => {
  const rewards = ref([]);
  const isLoading = ref(false);

  async function fetchExclusiveRewards() {
    isLoading.value = true;
    try {
      // The new apiClient returns data directly
      const data = await apiClient.get('/loyalty/exclusive-rewards');
      rewards.value = data;
    } catch (error) {
      // Error notification is handled by the API client's interceptor
      console.error("Failed to fetch rewards:", error);
      rewards.value = []; // Ensure rewards list is cleared on error
    } finally {
      isLoading.value = false;
    }
  }

  async function redeemReward(rewardId) {
    const notificationStore = useNotificationStore();
    try {
      await apiClient.post('/loyalty/redeem-reward', { reward_id: rewardId });
      notificationStore.showNotification({
        message: 'Reward redeemed successfully!',
        type: 'success'
      });
      return true;
    } catch (error) {
      console.error("Failed to redeem reward:", error);
      return false;
    }
  }

  return { rewards, isLoading, fetchExclusiveRewards, redeemReward };
});