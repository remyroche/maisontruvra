import { ref, watch } from 'vue';
import { apiClient } from '@/services/api';

/**
 * A Vue composable to simplify fetching data from an API endpoint.
 * It handles loading states, errors, and re-fetching when dependencies change.
 *
 * @param {Function} apiCall - The function that returns an API promise (e.g., () => apiClient.get('/products')).
 * @param {import('vue').Ref|null} watchSource - An optional ref to watch for changes. When it changes, the API call is re-triggered.
 * @returns {{data: import('vue').Ref, isLoading: import('vue').Ref, error: import('vue').Ref, fetchData: Function}}
 */
export function useApiData(apiCall, watchSource = null) {
  const data = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  const fetchData = async () => {
    isLoading.value = true;
    error.value = null;
    data.value = null;

    try {
      const response = await apiCall();
      data.value = response.data;
    } catch (err) {
      console.error('API call failed:', err);
      error.value = err.response?.data?.message || 'An unexpected error occurred.';
    } finally {
      isLoading.value = false;
    }
  };

  if (watchSource) {
    // Watch for changes in the source (e.g., a prop like productId) and re-fetch data.
    watch(watchSource, fetchData, { immediate: true });
  } else {
    // If there's no dependency to watch, fetch data immediately.
    fetchData();
  }

  return {
    data,
    isLoading,
    error,
    fetchData, // Also return the function so it can be called manually if needed
  };
}
