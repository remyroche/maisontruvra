import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminAssetsStore = defineStore('adminAssets', {
  state: () => ({
    assets: [],
    error: null,
  }),
  actions: {
    async fetchAssets() {
      try {
        const response = await apiClient.get('/assets');
        this.assets = response.data;
      } catch (error) {
        this.error = 'Failed to fetch assets.';
      }
    },
    async uploadAsset(file) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        await apiClient.post('/assets', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        await this.fetchAssets();
      } catch (error) {
        this.error = 'Failed to upload asset.';
      }
    },
    async deleteAsset(assetId) {
      try {
        await apiClient.delete(`/assets/${assetId}`);
        await this.fetchAssets();
      } catch (error) {
        this.error = 'Failed to delete asset.';
      }
    },
  },
});
