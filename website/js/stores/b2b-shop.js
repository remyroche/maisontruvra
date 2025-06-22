import { defineStore } from 'pinia';
import apiClient from '../api-client';

export const useB2BShopStore = defineStore('b2bShop', {
  state: () => ({
    products: [],
    categories: [],
    lastOrderItems: [],
    isLoading: true,
    error: null,
  }),
  actions: {
    async fetchShopData() {
      this.isLoading = true;
      this.error = null;
      try {
        // This single endpoint should provide all the necessary data for the shop page
        const response = await apiClient.get('/api/b2b/shop-data');
        const data = response.data;
        this.products = data.products;
        this.categories = data.categories;
        this.lastOrderItems = data.last_order_items;
      } catch (err) {
        console.error("Failed to fetch shop data:", err);
        this.error = err;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
