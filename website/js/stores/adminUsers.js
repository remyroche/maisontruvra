import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    users: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchUsers(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/users', { params });
        this.users = response.data;
      } catch (e) {
        this.error = 'Failed to fetch users.';
      } finally {
        this.isLoading = false;
      }
    },
    async createUser(userData) {
      await apiClient.post('/users', userData);
    },
    async updateUser(id, userData) {
      await apiClient.put(`/users/${id}`, userData);
    },
    async softDeleteUser(id) {
      await apiClient.delete(`/users/${id}/soft-delete`);
    },
    async hardDeleteUser(id) {
      await apiClient.delete(`/users/${id}/hard-delete`);
    },
    async freezeUser(userId) {
        await apiClient.post(`/sessions/user/${userId}/freeze`);
    },
    async unfreezeUser(userId) {
        await apiClient.post(`/sessions/user/${userId}/unfreeze`);
    }
  },
});

