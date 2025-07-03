// website/src/stores/adminRecommendations.js
// Pinia store for managing admin recommendation data

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
// Import the API client - we'll use the default export from api.js
import api from '@/services/api';
import { useNotificationStore } from './notification';

export const useAdminRecommendationsStore = defineStore('adminRecommendations', () => {
  // State
  const loading = ref(false);
  const summary = ref(null);
  const allRecommendations = ref([]);
  const pagination = ref({
    page: 1,
    per_page: 50,
    total_users: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });
  const selectedUsers = ref([]);
  const searchResults = ref([]);
  const searchLoading = ref(false);
  const bulkOperationStatus = ref(null);

  // Getters
  const hasRecommendations = computed(() => allRecommendations.value.length > 0);
  const selectedUserCount = computed(() => selectedUsers.value.length);
  const canPerformBulkOperations = computed(() => selectedUserCount.value > 0 && selectedUserCount.value <= 100);

  // Actions
  const fetchSummary = async () => {
    loading.value = true;
    try {
      const response = await api.adminGetRecommendationsSummary();
      summary.value = response.data;
      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: 'Failed to fetch recommendations summary',
        type: 'error'
      });
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const fetchAllRecommendations = async (options = {}) => {
    loading.value = true;
    try {
      const params = {
        page: options.page || pagination.value.page,
        per_page: options.per_page || pagination.value.per_page,
        limit_per_user: options.limit_per_user || 5
      };

      const response = await api.adminGetAllCustomerRecommendations(params);
      
      allRecommendations.value = response.data.recommendations;
      pagination.value = response.data.pagination;
      
      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: 'Failed to fetch customer recommendations',
        type: 'error'
      });
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const fetchUserRecommendations = async (userId, limit = 5) => {
    try {
      const response = await api.adminGetUserRecommendations(userId, { limit });
      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: `Failed to fetch recommendations for user ${userId}`,
        type: 'error'
      });
      throw error;
    }
  };

  const searchUsers = async (query, limit = 20) => {
    if (!query.trim()) {
      searchResults.value = [];
      return;
    }

    searchLoading.value = true;
    try {
      const response = await api.adminSearchUsers({ q: query, limit });
      searchResults.value = response.data.users;
      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: 'Failed to search users',
        type: 'error'
      });
      searchResults.value = [];
      throw error;
    } finally {
      searchLoading.value = false;
    }
  };

  const bulkGenerateRecommendations = async (userIds, limitPerUser = 5) => {
    if (!userIds.length || userIds.length > 100) {
      throw new Error('Invalid number of users selected');
    }

    loading.value = true;
    bulkOperationStatus.value = null;

    try {
      const response = await api.adminBulkGenerateRecommendations({
        user_ids: userIds,
        limit_per_user: limitPerUser
      });

      bulkOperationStatus.value = response.data;
      
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: `Bulk operation completed: ${response.data.successful} successful, ${response.data.failed} failed`,
        type: response.data.failed > 0 ? 'warning' : 'success'
      });

      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: 'Bulk recommendation generation failed',
        type: 'error'
      });
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const exportRecommendations = async (format = 'json', options = {}) => {
    try {
      const params = {
        format,
        limit_per_user: options.limit_per_user || 5,
        page: options.page || 1,
        per_page: options.per_page || 100
      };

      const response = await api.adminExportRecommendations({
        ...params,
        responseType: format === 'csv' ? 'blob' : 'json'
      });

      if (format === 'csv') {
        // Handle CSV download
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `customer_recommendations_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        const notificationStore = useNotificationStore();
        notificationStore.addNotification({
          message: 'Recommendations exported successfully',
          type: 'success'
        });
      }

      return response.data;
    } catch (error) {
      const notificationStore = useNotificationStore();
      notificationStore.addNotification({
        message: 'Failed to export recommendations',
        type: 'error'
      });
      throw error;
    }
  };

  // User selection management
  const toggleUserSelection = (userId) => {
    const index = selectedUsers.value.indexOf(userId);
    if (index > -1) {
      selectedUsers.value.splice(index, 1);
    } else {
      selectedUsers.value.push(userId);
    }
  };

  const selectAllUsers = () => {
    selectedUsers.value = allRecommendations.value.map(rec => rec.user_id);
  };

  const clearSelection = () => {
    selectedUsers.value = [];
  };

  const isUserSelected = (userId) => {
    return selectedUsers.value.includes(userId);
  };

  // Pagination helpers
  const goToPage = async (page) => {
    if (page >= 1 && page <= pagination.value.total_pages) {
      await fetchAllRecommendations({ page });
    }
  };

  const nextPage = async () => {
    if (pagination.value.has_next) {
      await goToPage(pagination.value.page + 1);
    }
  };

  const prevPage = async () => {
    if (pagination.value.has_prev) {
      await goToPage(pagination.value.page - 1);
    }
  };

  // Reset store
  const reset = () => {
    loading.value = false;
    summary.value = null;
    allRecommendations.value = [];
    pagination.value = {
      page: 1,
      per_page: 50,
      total_users: 0,
      total_pages: 0,
      has_next: false,
      has_prev: false
    };
    selectedUsers.value = [];
    searchResults.value = [];
    searchLoading.value = false;
    bulkOperationStatus.value = null;
  };

  return {
    // State
    loading,
    summary,
    allRecommendations,
    pagination,
    selectedUsers,
    searchResults,
    searchLoading,
    bulkOperationStatus,

    // Getters
    hasRecommendations,
    selectedUserCount,
    canPerformBulkOperations,

    // Actions
    fetchSummary,
    fetchAllRecommendations,
    fetchUserRecommendations,
    searchUsers,
    bulkGenerateRecommendations,
    exportRecommendations,
    toggleUserSelection,
    selectAllUsers,
    clearSelection,
    isUserSelected,
    goToPage,
    nextPage,
    prevPage,
    reset
  };
});