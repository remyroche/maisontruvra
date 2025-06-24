/*
 * FILENAME: website/js/stores/adminSystem.js
 * DESCRIPTION: Pinia store for various system management tasks.
 * UPDATED: Implemented functionality for Roles, Sessions, and Passports.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminSystemStore = defineStore('adminSystem', () => {
    const roles = ref([]);
    const sessions = ref([]);
    const passports = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchRoles() { 
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.get('/user-management/roles');
            roles.value = response.data.roles;
        } catch(err) { error.value = 'Failed to fetch roles.'; } 
        finally { isLoading.value = false; }
    }
    async function updateRole(id, data) { 
        // ... API call to update a role and its permissions
    }

    async function fetchSessions() { 
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.get('/sessions');
            sessions.value = response.data.sessions;
        } catch(err) { error.value = 'Failed to fetch sessions.'; } 
        finally { isLoading.value = false; }
    }
    async function terminateSession(id) { 
        // ... API call to terminate a session
    }

    async function fetchPassports() { 
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.get('/passports');
            passports.value = response.data.passports;
        } catch(err) { error.value = 'Failed to fetch passports.'; } 
        finally { isLoading.value = false; }
    }

    return { roles, sessions, passports, isLoading, error, fetchRoles, updateRole, fetchSessions, terminateSession, fetchPassports };
});
