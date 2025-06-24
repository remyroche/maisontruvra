import { defineStore } from 'pinia';
import apiClient from '../api-client';
import { ref } from 'vue';
import { debounce } from 'lodash-es';

export const useSearchStore = defineStore('search', () => {
  const isOverlayOpen = ref(false);
  const query = ref('');
  const results = ref([]);
  const loading = ref(false);
  const error = ref(null);

  function openOverlay() {
    isOverlayOpen.value = true;
    // Optional: focus the search input when overlay opens
    // This requires coordination with the component, often via an event bus or a ref.
  }

  function closeOverlay() {
    isOverlayOpen.value = false;
    query.value = '';
    results.value = [];
    error.value = null;
  }

  // Use debounce to prevent API calls on every keystroke
  const performSearch = debounce(async () => {
    if (query.value.length < 2) {
      results.value = [];
      return;
    }
    loading.value = true;
    error.value = null;
    try {
        // We will add this 'searchProducts' method to the apiClient
        const response = await apiClient.searchProducts(query.value);
        results.value = response.products || [];
    } catch (e) {
      error.value = 'Erreur lors de la recherche.';
      results.value = [];
      console.error('Search failed:', e);
    } finally {
      loading.value = false;
    }
  }, 300); // 300ms delay

  function setQuery(newQuery) {
    query.value = newQuery;
    performSearch();
  }

  return {
    isOverlayOpen,
    query,
    results,
    loading,
    error,
    openOverlay,
    closeOverlay,
    setQuery,
    performSearch
  };
});
