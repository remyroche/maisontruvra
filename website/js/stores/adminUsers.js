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

export const useAdminUserStore = defineStore('adminUsers', () => {
  // --- STATE ---
  const users = ref([]); // Holds the list of all users
  const isLoading = ref(false); // Tracks loading state for user operations
  const error = ref(null); // Holds the last error related to user management

  // --- ACTIONS ---
  
  /**
   * Fetches the complete list of users from the backend.
   */
  async function fetchUsers() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.get('/user-management/users');
      users.value = response.data.users;
    } catch (err) {
      console.error('Failed to fetch users:', err);
      error.value = 'An error occurred while fetching the user list.';
      if (err.response && err.response.status === 401) {
        const authStore = useAdminAuthStore();
        authStore.logout();
      }
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Creates a new user.
   * @param {object} userData - The new user's data.
   */
  async function createUser(userData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.post('/user-management/users', userData);
      // Add the new user to the top of the list for immediate feedback
      users.value.unshift(response.data.user);
      
      // --- LOGGING ---
      // The backend POST /user-management/users endpoint should call AuditLogService
      // to record this 'user_create' event.
      return true;
    } catch (err) {
      console.error('Failed to create user:', err);
      error.value = `Failed to create user: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

                                               /**
   * Updates a user's data.
   * @param {number} userId - The ID of the user to update.
   * @param {object} userData - The user data to update.
   */
  async function updateUser(userId, userData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/user-management/users/${userId}`, userData);
      const index = users.value.findIndex(u => u.id === userId);
      if (index !== -1) {
        users.value[index] = response.data.user;
      }
      
      // --- LOGGING ---
      // The backend PUT /user-management/users/{userId} endpoint should call AuditLogService
      // to record 'user_update' with details of the changes.
      return true;
    } catch (err) {
      console.error(`Failed to update user ${userId}:`, err);
      error.value = `Failed to update user: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Deletes a user.
   * @param {number} userId - The ID of the user to delete.
   */
  async function deleteUser(userId) {
    isLoading.value = true;
    error.value = null;
    try {
      await adminApiClient.delete(`/user-management/users/${userId}`);
      // Remove the user from the local state
      users.value = users.value.filter(u => u.id !== userId);

      // --- LOGGING ---
      // The backend DELETE /user-management/users/{userId} endpoint should call
      // AuditLogService to record this 'user_delete' event.
      return true;
    } catch (err) {
      console.error(`Failed to delete user ${userId}:`, err);
      error.value = `Failed to delete user: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

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
