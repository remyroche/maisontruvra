import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminCollectionsStore = defineStore('adminCollections', {
  state: () => ({
    collections: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCollections() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/product-collections');
        this.collections = response.data;
      } catch (e) {
        this.error = 'Failed to fetch product collections.';
      } finally {
        this.isLoading = false;
      }
    },
    async createCollection(collectionData) {
        try {
            await apiClient.post('/product-collections', collectionData);
            await this.fetchCollections();
        } catch (e) {
            this.error = 'Failed to create product collection.';
            throw e;
        }
    },
    async updateCollection(id, collectionData) {
        try {
            await apiClient.put(`/product-collections/${id}`, collectionData);
            await this.fetchCollections();
        } catch (e) {
            this.error = 'Failed to update product collection.';
            throw e;
        }
    },
    async deleteCollection(id) {
        try {
            await apiClient.delete(`/product-collections/${id}`);
            await this.fetchCollections();
        } catch (e) {
            this.error = 'Failed to delete product collection.';
        }
    },
  },
});

