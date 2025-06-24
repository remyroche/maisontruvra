/*
 * FILENAME: website/js/stores/adminLoyalty.js
 * DESCRIPTION: Pinia store for managing loyalty tiers.
 * UPDATED: Added full CRUD functionality for loyalty tiers.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminLoyaltyStore = defineStore('adminLoyalty', () => {
    const tiers = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchTiers() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/loyalty/tiers');
            tiers.value = response.data.tiers;
        } catch (err) {
            error.value = 'Failed to fetch loyalty tiers.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    async function createTier(data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.post('/loyalty/tiers', data);
            tiers.value.push(response.data.tier);
            return true;
        } catch(err) {
            error.value = `Failed to create tier: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    async function updateTier(id, data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.put(`/loyalty/tiers/${id}`, data);
            const index = tiers.value.findIndex(t => t.id === id);
            if(index !== -1) tiers.value[index] = response.data.tier;
            return true;
        } catch(err) {
            error.value = `Failed to update tier: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    async function deleteTier(id) {
        isLoading.value = true; error.value = null;
        try {
            await adminApiClient.delete(`/loyalty/tiers/${id}`);
            tiers.value = tiers.value.filter(t => t.id !== id);
            return true;
        } catch(err) {
            error.value = `Failed to delete tier: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }
    
    return { tiers, isLoading, error, fetchTiers, createTier, updateTier, deleteTier };
});
