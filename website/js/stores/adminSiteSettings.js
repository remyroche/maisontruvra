/*
 * FILENAME: website/js/stores/adminSiteSettings.js
 * DESCRIPTION: Pinia store for managing site-wide settings.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminSiteSettingsStore = defineStore('adminSiteSettings', () => {
    const settings = ref({});
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchSettings() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/site-management/settings');
            settings.value = response.data.settings;
        } catch (err) {
            error.value = 'Failed to fetch site settings.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    async function updateSettings(data) {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.put('/site-management/settings', data);
            settings.value = response.data.settings;
            return true;
        } catch (err) {
             error.value = 'Failed to update settings.';
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    
    return { settings, isLoading, error, fetchSettings, updateSettings };
});
