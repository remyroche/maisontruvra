import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminAuditLogStore = defineStore('adminAuditLog', {
  state: () => ({
    logs: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchLogs(filters = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/audit-log', { params: filters });
        this.logs = response.data;
      } catch (e) {
        this.error = 'Failed to fetch audit logs.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
