// website/src/stores/adminInventory.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from './notification';

/**
 * Manages state for the new Item-based inventory system in the admin panel.
 */
export const useAdminInventoryStore = defineStore('adminInventory', () => {
  // --- STATE ---
  const items = ref([]); // A flat list of all individual items
  const loading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  /**
   * Fetches all individual inventory items from the backend.
   */
  async function fetchAllItems() {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/admin/inventory/items');
      items.value = response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to fetch inventory items.';
      error.value = errorMessage;
      useNotificationStore().addNotification(errorMessage, 'error');
    } finally {
      loading.value = false;
    }
  }

  /**
   * Creates a single new inventory item.
   * @param {object} itemData - The data for the new item from ItemForm.vue.
   */
  async function createItem(itemData) {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post('/admin/inventory/items', itemData);
      // Add the new item to the top of the list for immediate feedback
      items.value.unshift(response.data);
      useNotificationStore().addNotification('Inventory item created successfully!', 'success');
      return true; // Indicate success
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to create inventory item.';
      error.value = errorMessage;
      useNotificationStore().addNotification(errorMessage, 'error');
      return false; // Indicate failure
    } finally {
      loading.value = false;
    }
  }

  /**
   * Creates a batch of new inventory items.
   * @param {object} batchData - The data for the new batch from BatchItemForm.vue.
   */
  async function createItemBatch(batchData) {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post('/admin/inventory/items/batch', batchData);
      // Add all newly created items to the top of the list
      items.value.unshift(...response.data);
      useNotificationStore().addNotification(`${response.data.length} items created successfully in a batch!`, 'success');
      return true; // Indicate success
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to create item batch.';
      error.value = errorMessage;
      useNotificationStore().addNotification(errorMessage, 'error');
      return false; // Indicate failure
    } finally {
      loading.value = false;
    }
  }

  // Expose state and actions
  return {
    items,
    loading,
    error,
    fetchAllItems,
    createItem,
    createItemBatch, // Expose the new action
  };
});
