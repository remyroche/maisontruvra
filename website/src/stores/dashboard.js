import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '@/services/api';

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchDashboardData() {
    isLoading.value = true;
    error.value = null;
    try {
      // The API client's interceptor will return the data directly
      data.value = await apiClient.get('/account/dashboard');
    } catch (e) {
      error.value = "Failed to load dashboard data.";
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  return { data, isLoading, error, fetchDashboardData };
});