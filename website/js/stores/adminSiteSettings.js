/*
 * FILENAME: website/js/stores/adminSiteSettings.js
 * DESCRIPTION: Pinia store for managing site-wide settings.
 * UPDATED: Fully implemented with fetch and update actions.
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
            // The backend sends an array, let's convert it to an object for easier access
            settings.value = response.data.settings.reduce((obj, item) => {
                obj[item.key] = item.value;
                return obj;
            }, {});
        } catch (err) {
            error.value = 'Failed to fetch site settings.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    async function updateSettings(settingsData) {
        isLoading.value = true;
        error.value = null;
        try {
            // Convert back to array of key-value pairs for the backend
            const payload = Object.keys(settingsData).map(key => ({ key, value: settingsData[key] }));
            const response = await adminApiClient.put('/site-management/settings', { settings: payload });
            settings.value = response.data.settings.reduce((obj, item) => {
                obj[item.key] = item.value;
                return obj;
            }, {});
            // --- LOGGING ---
            // The backend should log this 'site_settings_update' event.
            return true;
        } catch (err) {
             error.value = `Failed to update settings: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    
    return { settings, isLoading, error, fetchSettings, updateSettings };
});
