import { defineStore } from 'pinia';
import apiClient from '../api-client';
import { ref } from 'vue';
import { debounce } from 'lodash-es';

export const useB2BSearchStore = defineStore('b2bSearch', () => {
  const isOverlayOpen = ref(false);
  const query = ref('');
  const results = ref([]);
  const loading = ref(false);
  const error = ref(null);

  function openOverlay() {
    isOverlayOpen.value = true;
  }

  function closeOverlay() {
    isOverlayOpen.value = false;
    query.value = '';
    results.value = [];
    error.value = null;
  }

  const performSearch = debounce(async () => {
    if (query.value.length < 2) {
      results.value = [];
      return;
    }
    loading.value = true;
    error.value = null;
    try {
        // This will call a new method specific to B2B search
        const response = await apiClient.searchB2BProducts(query.value);
        results.value = response.products || [];
    } catch (e) {
      error.value = 'Erreur lors de la recherche B2B.';
      results.value = [];
      console.error('B2B Search failed:', e);
    } finally {
      loading.value = false;
    }
  }, 300); // 300ms debounce

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
