/*
 * FILENAME: website/js/stores/adminUsers.js
 * DESCRIPTION: Pinia store for managing user data in the Admin Portal.
 *
 * This store handles all state and operations for the 'Manage Users' page,
 * including fetching the user list and performing CRUD operations. It demonstrates
 * loading and error state management for a specific feature.
 *
 * UPDATED: Added `createUser` and `deleteUser` actions to complete the
 * CRUD functionality for the user management feature.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';
import { useAdminAuthStore } from './adminAuth';


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

    // These actions are now in the adminSystem store, but we can keep wrappers for convenience
    async freezeUser(userId) {
        const systemStore = useAdminSystemStore();
        await systemStore.freezeUser(userId);
        await this.fetchUsers();
    },

    async unfreezeUser(userId) {
        const systemStore = useAdminSystemStore();
        await systemStore.unfreezeUser(userId);
        await this.fetchUsers();
    }
  },
});

  return {
    users,
    isLoading,
    error,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
  };
});
