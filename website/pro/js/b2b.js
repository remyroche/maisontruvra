import { defineStore } from 'pinia';
import apiClient from '../api-client';

export const useB2BStore = defineStore('b2b', {
  state: () => ({
    products: [],
    profile: null,
    invoices: [],
    dashboardData: null,
    isLoading: false,
  }),

  actions: {
    async fetchProducts() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/b2b/products');
        this.products = response.data;
      } catch (error) {
        console.error('Failed to fetch B2B products:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    async fetchProfile() {
        this.isLoading = true;
        try {
            const response = await apiClient.get('/b2b/profile');
            this.profile = response.data;
        } catch (error) {
            console.error('Failed to fetch profile:', error);
        } finally {
            this.isLoading = false;
        }
    },

    async updateProfile(profileData) {
        this.isLoading = true;
        try {
            const response = await apiClient.post('/b2b/profile', profileData);
            this.profile = { ...this.profile, ...profileData };
            // Optionally show a success message to the user
            return response.data;
        } catch (error) {
            console.error('Failed to update profile:', error);
            // Optionally show an error message
            throw error;
        } finally {
            this.isLoading = false;
        }
    },

    // ... other actions for invoices, dashboard, etc.
  },
});
