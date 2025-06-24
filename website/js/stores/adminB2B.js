/*
 * FILENAME: website/js/stores/adminB2B.js
 * DESCRIPTION: Pinia store for managing B2B accounts.
 * UPDATED: Added full functionality for fetching and managing B2B accounts.
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
            const response = await adminApiClient.get('/b2b-management/accounts');
            accounts.value = response.data.accounts;
        } catch (err) {
            error.value = 'Failed to fetch B2B accounts.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    async function updateAccountStatus(accountId, is_approved) {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.put(`/b2b-management/accounts/${accountId}/status`, { is_approved });
            const index = accounts.value.findIndex(a => a.id === accountId);
            if (index !== -1) {
                accounts.value[index] = response.data.account;
            }
            // --- LOGGING ---
            // The backend should log this approval/rejection event.
            return true;
        } catch (err) {
            error.value = `Failed to update B2B account status: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    
    return { accounts, isLoading, error, fetchAccounts, updateAccountStatus };
});
