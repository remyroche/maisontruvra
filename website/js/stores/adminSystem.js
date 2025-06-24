/*
 * FILENAME: website/js/stores/adminSystem.js
 * DESCRIPTION: New Pinia store for various system management tasks like Roles and Sessions.
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

    async function fetchRoles() { /* ... */ }
    async function createRole(data) { /* ... */ }
    async function updateRole(id, data) { /* ... */ }
    async function deleteRole(id) { /* ... */ }

    async function fetchSessions() { /* ... */ }
    async function terminateSession(id) { /* ... */ }

    async function fetchPassports() { /* ... */ }

    return { roles, sessions, passports, isLoading, error, fetchRoles, createRole, updateRole, deleteRole, fetchSessions, terminateSession, fetchPassports };
});
