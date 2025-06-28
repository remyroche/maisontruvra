import { defineStore } from 'pinia';
import adminApiClient from '@/common/adminApiClient';

export const useAdminCatalogStore = defineStore('adminCatalog', {
  state: () => ({
    products: [],
    categories: [],
    collections: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    // === PRODUCTS ===
    async fetchProducts() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await adminApiClient.get('/products');
        this.products = response.data;
      } catch (error) {
        this.error = 'Failed to fetch products.';
      } finally {
        this.isLoading = false;
      }
    },
    async createProduct(productData) {
      // API call to create product
    },
    async updateProduct(productId, productData) {
      // API call to update product
    },

    // === CATEGORIES ===
    async fetchCategories() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await adminApiClient.get('/product-management/categories');
        this.categories = response.data;
      } catch (error) {
        this.error = 'Failed to fetch categories.';
      } finally {
        this.isLoading = false;
      }
    },
    async createCategory(categoryData) {
      // API call to create category
    },

    // === COLLECTIONS ===
    async fetchCollections() {
       this.isLoading = true;
      this.error = null;
      try {
        const response = await adminApiClient.get('/product-management/collections');
        this.collections = response.data;
      } catch (error) {
        this.error = 'Failed to fetch collections.';
      } finally {
        this.isLoading = false;
      }
    },
    async createCollection(collectionData) {
       // API call to create collection
    }
  }
});

