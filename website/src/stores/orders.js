// website/src/stores/orders.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from './notification';

/**
 * Manages state related to customer orders.
 */
export const useOrderStore = defineStore('orders', () => {
  // --- STATE ---
  const orders = ref([]); // For the list of all user orders
  const currentOrder = ref(null); // For the detailed order view
  const loading = ref(false);
  const error = ref(null);

  // --- GETTERS ---
  // (No specific getters needed for now, but could be added later)

  // --- ACTIONS ---

  /**
   * Fetches the list of all orders for the currently authenticated user.
   */
  async function fetchUserOrders() {
    loading.value = true;
    error.value = null;
    try {
      // Assuming the backend has an endpoint like GET /api/account/orders
      const response = await api.get('/account/orders'); 
      orders.value = response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to fetch orders.';
      error.value = errorMessage;
      useNotificationStore().addNotification(errorMessage, 'error');
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetches the details of a single order by its ID.
   * @param {string|number} orderId - The ID of the order to fetch.
   */
  async function fetchOrderById(orderId) {
    loading.value = true;
    error.value = null;
    currentOrder.value = null; // Reset previous order details
    try {
      // Assuming the backend has an endpoint like GET /api/account/orders/<id>
      const response = await api.get(`/account/orders/${orderId}`);
      currentOrder.value = response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Could not find the specified order.';
      error.value = errorMessage;
      useNotificationStore().addNotification(errorMessage, 'error');
    } finally {
      loading.value = false;
    }
  }

  // Expose state and actions
  return {
    orders,
    currentOrder,
    loading,
    error,
    fetchUserOrders,
    fetchOrderById,
  };
});
