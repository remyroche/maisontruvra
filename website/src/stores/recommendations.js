// website/src/stores/recommendations.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';

/**
 * Manages state for personalized product recommendations.
 */
export const useRecommendationStore = defineStore('recommendations', () => {
  // --- STATE ---
  const recommendations = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  /**
   * Fetches personalized product recommendations for the current user.
   */
  async function fetchRecommendations() {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/api/recommendations');
      recommendations.value = response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to fetch recommendations.';
      error.value = errorMessage;
      // We don't show a notification here as it's not a critical failure
      console.error(errorMessage);
    } finally {
      loading.value = false;
    }
  }

  // Expose state and actions
  return {
    recommendations,
    loading,
    error,
    fetchRecommendations,
  };
});