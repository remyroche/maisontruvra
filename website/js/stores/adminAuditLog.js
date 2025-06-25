import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminAuditLogStore = defineStore('adminAuditLog', {
  state: () => ({
    logs: [],
    pagination: {
      total: 0,
      pages: 0,
      currentPage: 1,
      hasNext: false,
      hasPrev: false,
    },
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchLogs(page = 1, date_filter = null) {
      this.isLoading = true;
      this.error = null;
      try {
        const params = { page };
        if (date_filter) {
          params.date = date_filter;
        }
        const response = await apiClient.get('/audit-log', { params });
        this.logs = response.data.logs;
        this.pagination.total = response.data.total;
        this.pagination.pages = response.data.pages;
        this.pagination.currentPage = response.data.current_page;
        this.pagination.hasNext = response.data.has_next;
        this.pagination.hasPrev = response.data.has_prev;
      } catch (e) {
        this.error = 'Failed to fetch audit logs.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
