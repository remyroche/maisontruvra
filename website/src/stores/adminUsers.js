import { defineStore } from 'pinia';
import api from '@/services/api';
import { useNotificationStore } from './notification';

export const useAdminUsersStore = defineStore('adminUsers', {
  state: () => ({
    users: [],
    tiers: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchUsers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get('/admin/api/users/');
        // The user service should return comprehensive user data
        // For now, we assume it returns what we need. Let's call a different endpoint if needed.
        const usersResponse = await api.get('/admin/api/b2b/'); // This gives more detail for now
        this.users = usersResponse.data;

      } catch (error) {
        this.error = 'Failed to fetch users.';
        useNotificationStore().addNotification(this.error, 'error');
      } finally {
        this.isLoading = false;
      }
    },
    async fetchTiers() {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await api.get('/admin/api/b2b/tiers');
            this.tiers = response.data;
        } catch (error) {
            this.error = 'Failed to fetch tiers.';
            useNotificationStore().addNotification(this.error, 'error');
        } finally {
            this.isLoading = false;
        }
    },
    async assignTierToUser(userId, tierId) {
        const notificationStore = useNotificationStore();
        try {
            const response = await api.post(`/admin/api/users/${userId}/assign-tier`, { tier_id: tierId });
            notificationStore.addNotification('Tier assigned successfully!', 'success');
            await this.fetchUsers(); // Refresh user list
        } catch (error) {
            const message = error.response?.data?.message || 'Failed to assign tier.';
            notificationStore.addNotification(message, 'error');
        }
    },
    async setCustomDiscountForUser(userId, discountData) {
        const notificationStore = useNotificationStore();
        try {
            const response = await api.post(`/admin/api/users/${userId}/custom-discount`, {
                discount_percentage: discountData.discount,
                monthly_spend_limit: discountData.limit,
            });
            notificationStore.addNotification('Custom discount set successfully!', 'success');
            await this.fetchUsers(); // Refresh user list
        } catch (error) {
            const message = error.response?.data?.message || 'Failed to set custom discount.';
            notificationStore.addNotification(message, 'error');
        }
    },
  },
});
