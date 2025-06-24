/*
 * FILENAME: website/js/stores/adminLoyalty.js
 * DESCRIPTION: Pinia store for managing loyalty tiers.
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

    // ... CRUD actions for tiers
    
    return { tiers, isLoading, error, fetchTiers };
});
