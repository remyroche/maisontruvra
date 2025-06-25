import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminOrdersStore = defineStore('adminOrders', {
  state: () => ({
    orders: [],
    isLoading: false,
    error: null,
    pagination: {},
  }),
  actions: {
    async fetchOrders(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/orders', { params });
        this.orders = response.data.data; // Assuming paginated response
        this.pagination = {
            total: response.data.total,
            pages: response.data.pages,
            currentPage: response.data.current_page,
        };
      } catch (e) {
        console.error('Failed to fetch orders:', e);
        this.error = 'An unexpected error occurred while fetching orders.';
      } finally {
        this.isLoading = false;
      }
    },

    async updateOrderStatus(orderId, status) {
        this.isLoading = true;
        this.error = null;
        try {
            await apiClient.put(`/orders/${orderId}/status`, { status });
            await this.fetchOrders(); // Refresh the list
        } catch(e) {
            console.error('Failed to update order status:', e);
            this.error = e.response?.data?.error || 'Failed to update order status.';
            throw this.error;
        } finally {
            this.isLoading = false;
        }
    },

    async softDeleteOrder(orderId) {
      this.error = null;
      try {
        await apiClient.delete(`/orders/${orderId}`);
        await this.fetchOrders();
      } catch (e) {
        console.error('Failed to soft delete order:', e);
        this.error = 'Could not soft-delete the order.';
        throw this.error;
      }
    },

    async hardDeleteOrder(orderId) {
      this.error = null;
      try {
        await apiClient.delete(`/orders/${orderId}?hard=true`);
        await this.fetchOrders();
      } catch (e) {
        console.error('Failed to hard delete order:', e);
        this.error = 'Could not permanently delete the order.';
        throw this.error;
      }
    },

    async restoreOrder(orderId) {
      this.error = null;
      try {
        await apiClient.put(`/orders/${orderId}/restore`);
        await this.fetchOrders();
      } catch (e) {
        console.error('Failed to restore order:', e);
        this.error = 'Could not restore the order.';
        throw this.error;
      }
    },
  },
});
