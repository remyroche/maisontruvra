import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from './notification';
import { useUserStore } from './user';

/**
 * Manages state and actions related to the B2B user experience,
 * including profile management, user invitations, and quote requests.
 */
export const useB2BStore = defineStore('b2b', () => {
  // --- STATE ---
  const profile = ref(null);
  const users = ref([]);
  const quotes = ref([]);
  const currentQuote = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  // --- Profile Management ---

  /**
   * Fetches the profile for the currently logged-in B2B account.
   */
  async function fetchB2BProfile() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get('/b2b/profile/');
      profile.value = response.data;
    } catch (err) {
      error.value = 'Failed to fetch B2B profile.';
      useNotificationStore().addNotification(error.value, 'error');
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Sends a request to soft-delete the B2B user's own account.
   * @returns {boolean} - True if the deletion request was successful.
   */
  async function deleteB2BAccount() {
    const notificationStore = useNotificationStore();
    const userStore = useUserStore();
    isLoading.value = true;
    try {
      const response = await api.delete('/b2b/profile/delete');
      notificationStore.addNotification(response.data.message, 'success');

      // Clear all relevant local state
      profile.value = null;
      userStore.user = null;
      userStore.isAuthenticated = false;
      
      return true;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to delete B2B account.';
      notificationStore.addNotification(errorMessage, 'error');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  // --- User Management within B2B Account ---

  /**
   * Fetches the list of users associated with the current B2B account.
   */
  async function fetchB2BUsers() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get('/b2b/profile/users');
      users.value = response.data;
    } catch (err) {
      error.value = 'Failed to fetch B2B users.';
      useNotificationStore().addNotification(error.value, 'error');
    } finally {
      isLoading.value = false;
    }
  }

  // --- Quote Management ---

  /**
   * Submits a new quote request.
   * @param {object} quoteData - The data for the quote request.
   */
  async function submitQuoteRequest(quoteData) {
    const notificationStore = useNotificationStore();
    isLoading.value = true;
    try {
      const response = await api.post('/b2b/quotes/request', quoteData);
      notificationStore.addNotification('Quote request submitted successfully!', 'success');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Quote request submission failed.';
      notificationStore.addNotification(errorMessage, 'error');
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetches the list of quotes for the current B2B account.
   */
  async function fetchB2BQuotes() {
    isLoading.value = true;
    error.value = null;
    try {
      // A B2B user should only be able to fetch their own quotes.
      const response = await api.get('/b2b/quotes'); 
      quotes.value = response.data;
    } catch (err) {
      error.value = 'Failed to fetch quotes.';
      useNotificationStore().addNotification(error.value, 'error');
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetches the details for a single quote.
   * @param {number} quoteId - The ID of the quote to fetch.
   */
  async function fetchB2BQuoteDetails(quoteId) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/b2b/quotes/${quoteId}`);
      currentQuote.value = response.data;
    } catch (err) {
      error.value = `Failed to fetch quote ${quoteId}.`;
      useNotificationStore().addNotification(error.value, 'error');
    } finally {
      isLoading.value = false;
    }
  }

  // Expose state and actions
  return {
    profile,
    users,
    quotes,
    currentQuote,
    isLoading,
    error,
    fetchB2BProfile,
    deleteB2BAccount,
    fetchB2BUsers,
    submitQuoteRequest,
    fetchB2BQuotes,
    fetchB2BQuoteDetails,
  };
});
