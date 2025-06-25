import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminDashboardStore = defineStore('adminDashboard', {
  state: () => ({
    stats: {},
    recentActivity: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchDashboardData() {
      this.isLoading = true;
      this.error = null;
      try {
        const [statsRes, activityRes] = await Promise.all([
          apiClient.get('/dashboard/stats'),
          apiClient.get('/dashboard/recent-activity')
        ]);
        this.stats = statsRes.data;
        this.recentActivity = activityRes.data;
      } catch (e) {
        this.error = 'Failed to fetch dashboard data.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
