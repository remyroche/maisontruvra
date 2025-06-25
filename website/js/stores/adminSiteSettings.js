import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminSiteSettingsStore = defineStore('adminSiteSettings', {
  state: () => ({
    settings: {},
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSettings() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/site-settings');
        this.settings = response.data;
      } catch (e) {
        this.error = 'Failed to fetch site settings.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async saveSettings(settingsData) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.post('/site-settings', settingsData);
            await this.fetchSettings(); // Refresh settings
        } catch (e) {
            this.error = 'Failed to save settings.';
            console.error(this.error, e);
            throw e;
        } finally {
            this.isLoading = false;
        }
    }
  },
});
