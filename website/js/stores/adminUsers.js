import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    users: [],
    user: null, // For single user details
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchUsers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/users');
        this.users = response.data;
      } catch (error) {
        this.error = 'Failed to fetch users.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUser(userId) {
        this.isLoading = true;
        this.error = null;
        try {
          const response = await apiClient.get(`/users/${userId}`);
          this.user = response.data;
          return this.user;
        } catch (error) {
          this.error = 'Failed to fetch user details.';
          console.error(this.error, error);
        } finally {
          this.isLoading = false;
        }
    },

    async createUser(userData) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.post('/users', userData);
        await this.fetchUsers(); // Refresh the user list
      } catch (error) {
        this.error = 'Failed to create user.';
        console.error(this.error, error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async updateUser(userId, userData) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.put(`/users/${userId}`, userData);
        await this.fetchUsers(); // Refresh the user list
      } catch (error) {
        this.error = 'Failed to update user.';
        console.error(this.error, error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    async deleteUser(userId) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.delete(`/users/${userId}`);
            await this.fetchUsers();
        } catch (error) {
            this.error = 'Failed to delete user.';
            console.error(this.error, error);
        } finally {
            this.isLoading = false;
        }
    },

    async freezeUser(userId) {
        this.isLoading = true;
        this.error = null;
        try {
            // This now calls the correct endpoint directly
            await apiClient.post(`/sessions/user/${userId}/freeze`);
            // Update the user's state in the list without a full refetch for better UX
            const user = this.users.find(u => u.id === userId);
            if (user) user.is_frozen = true;
        } catch (error) {
            this.error = 'Failed to freeze user.';
            console.error(this.error, error);
        } finally {
            this.isLoading = false;
        }
    },

    async unfreezeUser(userId) {
        this.isLoading = true;
        this.error = null;
        try {
            // This now calls the correct endpoint directly
            await apiClient.post(`/sessions/user/${userId}/unfreeze`);
            // Update the user's state in the list
            const user = this.users.find(u => u.id === userId);
            if (user) user.is_frozen = false;
        } catch (error) {
            this.error = 'Failed to unfreeze user.';
            console.error(this.error, error);
        } finally {
            this.isLoading = false;
        }
    }
  },
});
