import { defineStore } from 'pinia';
import adminApiClient from '@/common/adminApiClient';

export const useAdminInventoryStore = defineStore('adminInventory', {
  state: () => ({
    inventory: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchInventory() {
      this.loading = true;
      this.error = null;
      try {
        const response = await adminApiClient.get('/inventory');
        // Add a 'new_stock' property to each item for v-model binding
        this.inventory = response.data.map(item => ({...item, new_stock: item.stock_level }));
      } catch (error) {
        this.error = 'Failed to load inventory.';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    async updateStock(productId, newStockLevel) {
      // The PUT request should send the new stock level in its body
      try {
        const response = await adminApiClient.put(`/inventory/${productId}`, { stock_level: newStockLevel });
        // Update the local state to reflect the change immediately
        const index = this.inventory.findIndex(item => item.product_id === productId);
        if (index !== -1) {
          this.inventory[index].stock_level = response.data.stock_level;
          this.inventory[index].new_stock = response.data.stock_level;
        }
      } catch (error) {
        console.error(`Failed to update stock for product ${productId}:`, error);
        throw error; // Re-throw to be caught by the component
      }
    },
  },
});

&
