/*
 * FILENAME: website/js/stores/adminInventory.js
 * DESCRIPTION: Pinia store for managing product inventory levels.
 * UPDATED: Fully implemented with fetch and update actions.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminInventoryStore = defineStore('adminInventory', {
  state: () => ({
    inventory: [],
    error: null,
  }),
  actions: {
    async fetchInventory() {
      try {
        const response = await apiClient.get('/inventory');
        this.inventory = response.data;
      } catch (error) {
        this.error = 'Failed to fetch inventory.';
      }
    },
    async updateStock(productId, newStock) {
      try {
        await apiClient.put(`/inventory/${productId}`, { stock: newStock });
        await this.fetchInventory();
      } catch (error) {
        this.error = 'Failed to update stock.';
      }
    },
  },
});

    async function updateStock(productId, newStock) {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.put(`/inventory/stock/${productId}`, { stock_quantity: newStock });
            const index = inventory.value.findIndex(p => p.id === productId);
            if (index !== -1) {
                inventory.value[index].stock_quantity = response.data.stock_quantity;
            }
             // --- LOGGING ---
            // The backend should log this 'stock_update' event.
            return true;
        } catch (err) {
            error.value = 'Failed to update stock.';
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    return { inventory, isLoading, error, fetchInventory, updateStock };
