import { defineStore } from 'pinia';
import api from '@/services/api';

export const useProductStore = defineStore('products', {
  state: () => ({
    products: [],
    currentProduct: null,
    loading: false,
    error: null,
  }),
  
  actions: {
    /**
     * Fetches all public products from the API, with a simple caching mechanism.
     * @param {boolean} force - If true, forces a refetch even if data exists.
     */
    async fetchProducts(force = false) {
      if (this.products.length > 0 && !force) {
        console.log('Using cached products.');
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/products/');
        this.products = response.data;
      } catch (error) {
        this.error = 'Failed to fetch products.';
        console.error(this.error, error);
        // In a real app, you might use a dedicated notification store here.
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetches a single product by its ID and stores it in `currentProduct`.
     * @param {number} productId - The ID of the product to fetch.
     */
    async fetchProductById(productId) {
        this.loading = true;
        this.error = null;
        this.currentProduct = null;
        try {
            const response = await api.get(`/products/${productId}`);
            this.currentProduct = response.data;
        } catch(error) {
            this.error = `Failed to fetch product with ID: ${productId}`;
            console.error(this.error, error);
        } finally {
            this.loading = false;
        }
    },

    /**
     * Requests a back-in-stock notification for a given product.
     * @param {number} productId - The ID of the out-of-stock product.
     * @param {string} email - The user's email address for the notification.
     * @returns {Promise<object>} The API response message.
     */
    async requestStockNotification(productId, email) {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.post(`/products/${productId}/notify-me`, { email });
        return response.data;
      } catch (error) {
        const errorMessage = error.response?.data?.error || 'Failed to submit notification request.';
        this.error = errorMessage;
        console.error('Stock notification request failed:', error);
        throw new Error(errorMessage);
      } finally {
        this.loading = false;
      }
    },
  },
});
