/*
 * FILENAME: website/js/stores/adminProfile.js
 * DESCRIPTION: Pinia store for the admin's own profile management.
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
            authStore.adminUser.value = response.data.user; // Update user in auth store
            return true;
        } catch (err) {
            error.value = 'Failed to update profile.';
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    
    async function changePassword(data) {
        // ...
    }

    return { isLoading, error, updateProfile, changePassword };
});
