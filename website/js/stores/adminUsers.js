import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    users: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches a list of users from the API.
     * @param {object} params - Optional query parameters, e.g., { include_deleted: true }.
     */
    async fetchUsers(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/users', { params });
        this.users = response.data;
      } catch (e) {
        console.error('Failed to fetch users:', e);
        this.error = 'An unexpected error occurred while fetching users. Please try again.';
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Creates a new user.
     * @param {object} userData - The data for the new user.
     */
    async createUser(userData) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.post('/users', userData);
      } catch (e) {
        console.error('Failed to create user:', e);
        this.error = e.response?.data?.error || 'Failed to create user.';
        throw this.error; // Re-throw to allow components to handle the error
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Updates an existing user.
     * @param {number} id - The ID of the user to update.
     * @param {object} userData - The updated data for the user.
     */
    async updateUser(id, userData) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.put(`/users/${id}`, userData);
      } catch (e) {
        console.error('Failed to update user:', e);
        this.error = e.response?.data?.error || 'Failed to update user.';
        throw this.error;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Soft-deletes a user.
     * @param {number} id - The ID of the user to soft-delete.
     */
    async softDeleteUser(id) {
      this.error = null;
      try {
        await apiClient.delete(`/users/${id}/soft-delete`);
      } catch (e) {
        console.error('Failed to soft delete user:', e);
        this.error = 'Could not soft-delete the user. Please try again.';
        throw this.error;
      }
    },

    /**
     * Permanently deletes a user.
     * @param {number} id - The ID of the user to hard-delete.
     */
    async hardDeleteUser(id) {
      this.error = null;
      try {
        await apiClient.delete(`/users/${id}/hard-delete`);
      } catch (e) {
        console.error('Failed to hard delete user:', e);
        this.error = 'Could not permanently delete the user. Please try again.';
        throw this.error;
      }
    },

    /**
     * Restores a soft-deleted user.
     * @param {number} id - The ID of the user to restore.
     */
    async restoreUser(id) {
        this.error = null;
        try {
            await apiClient.put(`/users/${id}/restore`);
        } catch(e) {
            console.error('Failed to restore user:', e);
            this.error = 'Could not restore the user. Please try again.';
            throw this.error;
        }
    },

    /**
     * Freezes a user's account, preventing login.
     * @param {number} userId - The ID of the user to freeze.
     */
    async freezeUser(userId) {
        this.error = null;
        try {
            await apiClient.post(`/sessions/user/${userId}/freeze`);
            // Optimistically update UI for better responsiveness
            const user = this.users.find(u => u.id === userId);
            if (user) user.is_frozen = true;
        } catch(e) {
            console.error('Failed to freeze user:', e);
            this.error = 'Could not freeze the user account.';
            throw this.error;
        }
    },

    /**
     * Unfreezes a user's account, allowing login.
     * @param {number} userId - The ID of the user to unfreeze.
     */
    async unfreezeUser(userId) {
        this.error = null;
        try {
            await apiClient.post(`/sessions/user/${userId}/unfreeze`);
            // Optimistically update UI for better responsiveness
            const user = this.users.find(u => u.id === userId);
            if (user) user.is_frozen = false;
        } catch(e) {
            console.error('Failed to unfreeze user:', e);
            this.error = 'Could not unfreeze the user account.';
            throw this.error;
        }
    }
  },
});

