/*
 * FILENAME: website/js/stores/adminB2B.js
 * DESCRIPTION: Pinia store for managing B2B accounts.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminB2BStore = defineStore('adminB2B', () => {
    const accounts = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchAccounts() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/b2b-management');
            accounts.value = response.data.accounts;
        } catch (err) {
            error.value = 'Failed to fetch B2B accounts.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    async function approveAccount(id) {
        // ...
    }
    
    return { accounts, isLoading, error, fetchAccounts, approveAccount };
});
