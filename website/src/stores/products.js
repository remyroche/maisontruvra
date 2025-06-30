import { defineStore } from 'pinia';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

export const useProductStore = defineStore('products', {
  state: () => ({
    products: [],
    loading: false,
    error: null,
  }),
  
  actions: {
    /**
     * Fetches products from the API.
     * * Recommendation Implemented: This action includes a "fetch-if-not-present"
     * caching strategy. It checks if the product list has already been populated.
     * If it has, the action returns early, avoiding a redundant and unnecessary
     * API call. This improves performance, especially when users navigate
     * back and forth between pages that display the product list.
     * * @param {boolean} force - If true, forces a refetch even if data exists.
     */
    async fetchProducts(force = false) {
      // 1. Check if we already have products and we are not forcing a refresh
      if (this.products.length > 0 && !force) {
        console.log('Using cached products.');
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/products');
        this.products = response.data.products;
      } catch (error) {
        this.error = 'Failed to fetch products.';
        const notificationStore = useNotificationStore();
        notificationStore.addNotification('Error fetching products', 'error');
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetches a single product by its slug.
     * Note: This could also be cached if individual products are frequently accessed.
     * @param {string} slug - The slug of the product to fetch.
     * @returns {Promise<object|null>} The product data or null if not found.
     */
    async fetchProductBySlug(slug) {
        this.loading = true;
        this.error = null;
        try {
            const response = await api.get(`/products/${slug}`);
            return response.data;
        } catch(error) {
            this.error = `Failed to fetch product: ${slug}`;
            const notificationStore = useNotificationStore();
            notificationStore.addNotification('Error fetching product details.', 'error');
            return null;
        } finally {
            this.loading = false;
        }
    }
  },
});
