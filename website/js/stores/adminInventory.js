/*
 * FILENAME: website/js/stores/adminInventory.js
 * DESCRIPTION: Pinia store for managing product inventory levels.
 * UPDATED: Fully implemented with fetch and update actions.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminInventoryStore = defineStore('adminInventory', () => {
    const inventory = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchInventory() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/inventory');
            inventory.value = response.data.inventory;
        } catch (err) {
            error.value = 'Failed to fetch inventory data.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

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
