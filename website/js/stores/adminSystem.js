import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminSystemStore = defineStore('adminSystem', {
  state: () => ({
    roles: [],
    sessions: [],
    error: null,
  }),
  actions: {
    async fetchRoles() {
      try {
        const response = await apiClient.get('/roles');
        this.roles = response.data;
      } catch (error) {
        this.error = 'Failed to fetch roles.';
      }
    },
    async createRole(roleData) {
      try {
        await apiClient.post('/roles', roleData);
        await this.fetchRoles();
      } catch (error) {
        this.error = 'Failed to create role.';
      }
    },
    async updateRole(roleId, roleData) {
      try {
        await apiClient.put(`/roles/${roleId}`, roleData);
        await this.fetchRoles();
      } catch (error) {
        this.error = 'Failed to update role.';
      }
    },
    async deleteRole(roleId) {
      try {
        await apiClient.delete(`/roles/${roleId}`);
        await this.fetchRoles();
      } catch (error) {
        this.error = 'Failed to delete role.';
      }
    },
    async fetchSessions() {
      try {
        const response = await apiClient.get('/sessions');
        this.sessions = response.data;
      } catch (error) {
        this.error = 'Failed to fetch sessions.';
      }
    },
    async terminateSession(sessionId) {
      try {
        await apiClient.post(`/sessions/${sessionId}/terminate`);
        await this.fetchSessions();
      } catch (error) {
        this.error = 'Failed to terminate session.';
      }
    },
  },
});
