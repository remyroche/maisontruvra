/*
 * FILENAME: website/js/stores/adminProfile.js
 * DESCRIPTION: Pinia store for the admin's own profile management.
 * UPDATED: Fully implemented with profile and password update actions.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';
import { useAdminAuthStore } from './adminAuth';

export const useAdminProfileStore = defineStore('adminProfile', () => {
    const isLoading = ref(false);
    const error = ref(null);

    async function updateProfile(data) {
        isLoading.value = true;
        error.value = null;
        const authStore = useAdminAuthStore();
        try {
            const response = await adminApiClient.put('/auth/profile', data);
            authStore.adminUser = response.data.user; // Update user in auth store
            return true;
        } catch (err) {
            error.value = `Failed to update profile: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    
    async function changePassword(data) {
        isLoading.value = true;
        error.value = null;
        try {
            await adminApiClient.post('/auth/profile/change-password', data);
            // --- LOGGING ---
            // Backend should log this security event.
            return true;
        } catch (err) {
            error.value = `Failed to change password: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    return { isLoading, error, updateProfile, changePassword };
});
