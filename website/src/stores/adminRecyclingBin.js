import { defineStore } from 'pinia';
import api from '@/services/api';
import { useNotificationStore } from './notification';

export const useAdminRecyclingBinStore = defineStore('adminRecyclingBin', {
  state: () => ({
    items: [],
    logs: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSoftDeletedItems() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get('/admin/recycling-bin/');
        this.items = response.data;
      } catch (error) {
        this.error = 'Failed to fetch soft-deleted items.';
        useNotificationStore().addNotification(this.error, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    async restoreItem(itemType, itemId) {
      this.isLoading = true;
      try {
        await api.post('/admin/recycling-bin/restore', { item_type: itemType, item_id: itemId });
        useNotificationStore().addNotification('Item restored successfully.', 'success');
        // Refresh the list after restoring
        await this.fetchSoftDeletedItems();
      } catch (error) {
        const errorMessage = error.response?.data?.error || 'Failed to restore item.';
        this.error = errorMessage;
        useNotificationStore().addNotification(errorMessage, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    async hardDeleteItem(itemType, itemId) {
      this.isLoading = true;
      try {
        await api.delete('/admin/recycling-bin/hard-delete', { data: { item_type: itemType, item_id: itemId } });
        useNotificationStore().addNotification('Item permanently deleted.', 'success');
        // Refresh the list after deleting
        await this.fetchSoftDeletedItems();
      } catch (error) {
        const errorMessage = error.response?.data?.error || 'Failed to permanently delete item.';
        this.error = errorMessage;
        useNotificationStore().addNotification(errorMessage, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    async fetchDeletionLogs(itemType, itemId) {
        this.isLoading = true;
        this.logs = [];
        try {
            const response = await api.get(`/admin/recycling-bin/logs?item_type=${itemType}&item_id=${itemId}`);
            this.logs = response.data;
        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Failed to fetch deletion logs.';
            this.error = errorMessage;
            useNotificationStore().addNotification(errorMessage, 'error');
        } finally {
            this.isLoading = false;
        }
    }
  },
});
