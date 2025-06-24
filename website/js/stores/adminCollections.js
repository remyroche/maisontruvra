/*
 * FILENAME: website/js/stores/adminCollections.js
 * DESCRIPTION: Pinia store for managing product collections.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminCollectionStore = defineStore('adminCollections', () => {
  const collections = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchCollections() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.get('/product-management/collections');
      collections.value = response.data.collections;
    } catch (err) {
      error.value = 'Failed to fetch collections.';
      console.error(err);
    } finally {
      isLoading.value = false;
    }
  }

  async function createCollection(data) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.post('/product-management/collections', data);
      collections.value.unshift(response.data.collection);
      return true;
    } catch (err) {
      error.value = `Failed to create collection: ${err.response?.data?.message || 'error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateCollection(id, data) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/product-management/collections/${id}`, data);
      const index = collections.value.findIndex(c => c.id === id);
      if (index !== -1) collections.value[index] = response.data.collection;
      return true;
    } catch (err) {
      error.value = `Failed to update collection: ${err.response?.data?.message || 'error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteCollection(id) {
    isLoading.value = true;
    error.value = null;
    try {
      await adminApiClient.delete(`/product-management/collections/${id}`);
      collections.value = collections.value.filter(c => c.id !== id);
      return true;
    } catch (err) {
      error.value = `Failed to delete collection: ${err.response?.data?.message || 'error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return { collections, isLoading, error, fetchCollections, createCollection, updateCollection, deleteCollection };
});
