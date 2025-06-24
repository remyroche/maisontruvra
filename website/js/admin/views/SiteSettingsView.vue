<!--
 * FILENAME: website/js/admin/views/SiteSettingsView.vue
 * DESCRIPTION: View for managing global site settings.
-->
<template>
    <AdminLayout>
        <div class="space-y-6 max-w-4xl mx-auto">
            <header>
                <h1 class="text-3xl font-bold text-gray-800">Site Settings</h1>
                <p class="text-gray-500 mt-1">Manage global configuration for the website.</p>
            </header>
            
            <div v-if="settingsStore.isLoading" class="text-center py-10">Loading settings...</div>
            <div v-else-if="settingsStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ settingsStore.error }}</div>

            <form v-else @submit.prevent="handleSubmit" class="bg-white p-8 rounded-lg shadow-md space-y-6">
                <div>
                    <label for="site-name" class="block text-sm font-medium text-gray-700">Site Name</label>
                    <input type="text" id="site-name" v-model="formState.site_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                </div>
                 <div>
                    <label for="maintenance-mode" class="flex items-center">
                        <input type="checkbox" id="maintenance-mode" v-model="formState.maintenance_mode" class="h-4 w-4 text-indigo-600 rounded">
                        <span class="ml-2 text-sm font-medium text-gray-900">Enable Maintenance Mode</span>
                    </label>
                    <p class="text-xs text-gray-500 mt-1">If checked, the public-facing site will be unavailable to visitors.</p>
                </div>
                
                <div class="border-t pt-6 flex justify-end">
                    <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">
                        Save Settings
                    </button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAdminSiteSettingsStore } from '../../stores/adminSiteSettings';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';

const settingsStore = useAdminSiteSettingsStore();
const notificationStore = useAdminNotificationStore();

const formState = ref({
    site_name: '',
    maintenance_mode: false,
});

onMounted(() => {
    settingsStore.fetchSettings();
});

// When settings are loaded from the store, update the local form state.
watch(() => settingsStore.settings, (newSettings) => {
    formState.value.site_name = newSettings.site_name || '';
    formState.value.maintenance_mode = newSettings.maintenance_mode === 'true';
}, { deep: true });


const handleSubmit = async () => {
    const settingsToSave = {
        ...formState.value,
        maintenance_mode: String(formState.value.maintenance_mode) // Convert boolean to string for backend
    };
    const success = await settingsStore.updateSettings(settingsToSave);
    if (success) {
        notificationStore.addNotification({ type: 'success', title: 'Settings Updated' });
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Update Failed', message: settingsStore.error });
    }
};
</script>
