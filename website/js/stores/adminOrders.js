import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminOrdersStore = defineStore('adminOrders', {
  state: () => ({
    orders: [],
    order: null, // For a single order's details
    isLoading: false,
    error: null,
    // Available statuses for dropdowns
    statuses: ['pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded'],
  }),
  actions: {
    async fetchOrders(filters = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/orders', { params: filters });
        this.orders = response.data;
      } catch (error) {
        this.error = 'Failed to fetch orders.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchOrderDetails(orderId) {
      this.isLoading = true;
      this.order = null;
      this.error = null;
      try {
        const response = await apiClient.get(`/orders/${orderId}`);
        this.order = response.data;
        return this.order;
      } catch (error) {
        this.error = `Failed to fetch details for order #${orderId}.`;
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async updateOrderStatus(orderId, status) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.put(`/orders/${orderId}/status`, { status });
        // Refresh the single order details if it's being viewed
        if (this.order && this.order.id === orderId) {
          await this.fetchOrderDetails(orderId);
        }
        // Also refresh the list to reflect the change there
        await this.fetchOrders(); 
      } catch (error) {
        this.error = `Failed to update status for order #${orderId}.`;
        console.error(this.error, error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
