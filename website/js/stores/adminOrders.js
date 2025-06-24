/*
 * FILENAME: website/js/stores/adminOrders.js
 * DESCRIPTION: Pinia store for managing order data in the Admin Portal.
 *
 * This store handles all state and operations related to customer orders,
 * including fetching the list of orders and updating their status.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminOrderStore = defineStore('adminOrders', () => {
  // --- STATE ---
  const orders = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  /**
   * Fetches all orders from the backend.
   */
  async function fetchOrders() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.get('/orders');
      orders.value = response.data.orders;
    } catch (err) {
      console.error('Failed to fetch orders:', err);
      error.value = 'An error occurred while fetching the order list.';
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Updates the status of a specific order.
   * @param {number} orderId - The ID of the order to update.
   * @param {string} newStatus - The new status for the order.
   */
  async function updateOrderStatus(orderId, newStatus) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/orders/${orderId}/status`, { status: newStatus });
      const index = orders.value.findIndex(o => o.id === orderId);
      if (index !== -1) {
        orders.value[index] = response.data.order;
      }
      // --- LOGGING ---
      // The backend PUT endpoint should trigger the AuditLogService for 'order_status_update'.
      return true;
    } catch (err) {
      console.error(`Failed to update order status for order ${orderId}:`, err);
      error.value = `Failed to update order status: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    orders,
    isLoading,
    error,
    fetchOrders,
    updateOrderStatus,
  };
});
