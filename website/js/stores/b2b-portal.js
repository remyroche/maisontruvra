import { defineStore } from 'pinia';
import apiClient from '../api-client';

// A unified store to manage the state for the entire B2B portal
export const useB2BPortalStore = defineStore('b2bPortal', {
  state: () => ({
    // Dashboard Data
    dashboard: {
      kpis: { total_spent: 0, total_orders: 0, average_order_value: 0 },
      most_purchased_products: [],
      latest_products: [],
      recent_orders: [],
      isLoading: true,
      error: null,
    },
    // Loyalty Data
    loyalty: {
      tier: 'Collaborateur', rank_percentage: 0, next_tier: 'Partenaire', next_tier_percentage: 25,
      points_balance: 0, points_history: [], referral_code: '',
      referral_earnings: 0, referral_history: [],
      isLoading: true, error: null,
    },
    // Invoices Data
    invoices: {
      list: [], isLoading: true, error: null,
    },
    // Profile Data
    profile: {
        company_name: '', contact_name: '', email: '',
        phone_number: '', address: '', zip_code: '',
        city: '', country: '', siret: '',
        delivery_addresses: [],
        isLoading: true, error: null, message: ''
    }
  }),

  actions: {
    async fetchDashboardData() {
      this.dashboard.isLoading = true;
      try {
        const response = await apiClient.get('/api/b2b/dashboard-data');
        this.dashboard = { ...response.data, isLoading: false, error: null };
      } catch (err) { this.dashboard.error = err; } finally { this.dashboard.isLoading = false; }
    },

    async fetchLoyaltyData() {
        this.loyalty.isLoading = true;
        try {
            const response = await apiClient.get('/api/b2b/loyalty-data');
            this.loyalty = { ...response.data, isLoading: false, error: null };
        } catch (err) { this.loyalty.error = err; } finally { this.loyalty.isLoading = false; }
    },
    
    async fetchInvoices() {
        this.invoices.isLoading = true;
        try {
            const response = await apiClient.get('/api/b2b/invoices');
            this.invoices.list = response.data.invoices;
        } catch (err) { this.invoices.error = err; } finally { this.invoices.isLoading = false; }
    },

    async fetchProfileData() {
        this.profile.isLoading = true;
        this.profile.message = '';
        try {
            const response = await apiClient.get('/api/b2b/profile');
            this.profile = { ...this.profile, ...response.data, isLoading: false, message: '', error: null };
        } catch(err) { this.profile.error = "Could not load your profile."; } finally { this.profile.isLoading = false; }
    },

    async updateProfileData(profileData) {
        this.profile.message = '';
        this.profile.error = null;
        try {
            const response = await apiClient.put('/api/b2b/profile', profileData);
            this.profile.message = response.data.message || 'Profile updated successfully.';
            await this.fetchProfileData(); // Re-fetch to get the source of truth
        } catch (err) { this.profile.error = err.response?.data?.message || 'An error occurred while updating.'; }
    },

    async addDeliveryAddress(addressData) {
        try {
            const response = await apiClient.post('/api/b2b/addresses', addressData);
            this.profile.delivery_addresses.push(response.data.address);
        } catch (err) { console.error('Failed to add address', err); }
    },

    async deleteDeliveryAddress(addressId) {
        try {
            await apiClient.delete(`/api/b2b/addresses/${addressId}`);
            this.profile.delivery_addresses = this.profile.delivery_addresses.filter(a => a.id !== addressId);
        } catch (err) { console.error('Failed to delete address', err); }
    }
  },
});
