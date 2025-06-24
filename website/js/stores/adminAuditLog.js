/*
 * FILENAME: website/js/stores/adminAuditLog.js
 * DESCRIPTION: Pinia store for viewing the admin audit log.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminAuditLogStore = defineStore('adminAuditLog', () => {
    const logs = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchLogs() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/audit-log');
            logs.value = response.data.logs;
        } catch (err) {
            error.value = 'Failed to fetch audit logs.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }
    
    return { logs, isLoading, error, fetchLogs };
});
