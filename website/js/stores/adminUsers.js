/*
 * FILENAME: website/js/stores/adminUsers.js
 * DESCRIPTION: Pinia store for managing user data in the Admin Portal.
 *
 * This store handles all state and operations for the 'Manage Users' page,
 * including fetching the user list and performing CRUD operations. It demonstrates
 * loading and error state management for a specific feature.
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
      const response = await adminApiClient.get('/users');
      users.value = response.data.users;
    } catch (err) {
      console.error('Failed to fetch users:', err);
      error.value = 'An error occurred while fetching the user list.';
      // If unauthorized, the auth store should handle logout
      if (err.response && err.response.status === 401) {
        const authStore = useAdminAuthStore();
        authStore.logout();
      }
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Updates a user's data.
   * @param {number} userId - The ID of the user to update.
   * @param {object} userData - The user data to update { role, first_name, ... }.
   */
  async function updateUser(userId, userData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/users/${userId}`, userData);
      
      // Update the user in the local state
      const index = users.value.findIndex(u => u.id === userId);
      if (index !== -1) {
        users.value[index] = response.data.user;
      }

      // --- LOGGING ---
      // The backend's PUT /users/{userId} endpoint should call the
      // AuditLogService to record this 'user_update' event, including
      // what fields were changed.
      return true; // Indicate success
    } catch (err) {
      console.error(`Failed to update user ${userId}:`, err);
      error.value = `Failed to update user: ${err.response?.data?.message || 'Server error'}`;
      return false; // Indicate failure
    } finally {
      isLoading.value = false;
    }
  }

  return {
    users,
    isLoading,
    error,
    fetchUsers,
    updateUser,
  };
});
