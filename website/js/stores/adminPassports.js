import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminPassportsStore = defineStore('adminPassports', {
  state: () => ({
    passports: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchPassports() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/passports');
        this.passports = response.data;
      } catch (e) {
        this.error = 'Failed to fetch product passports.';
      } finally {
        this.isLoading = false;
      }
    },
    async downloadPassport(passportId) {
        try {
            const response = await apiClient.get(`/passports/${passportId}/download`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `passport_${passportId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch(e) {
            this.error = 'Failed to download passport.';
        }
    }
  },
});
