import { defineStore } from 'pinia';
import { ref } from 'vue';
import { adminApiClient } from '@/services/api';

export const useAdminLoyaltyStore = defineStore('adminLoyalty', () => {
  const tiers = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchTiers() {
    if (tiers.value.length > 0) return; // Avoid re-fetching if already loaded

    isLoading.value = true;
    error.value = null;
    try {
      const data = await adminApiClient.get('/loyalty/tiers');
      tiers.value = data;
    } catch (e) {
      error.value = 'Failed to fetch loyalty tiers.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  return { tiers, isLoading, error, fetchTiers };
});