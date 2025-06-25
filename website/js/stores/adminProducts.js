import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminProductsStore = defineStore('adminProducts', {
  state: () => ({
    products: [],
    product: null, // For a single product
    categories: [], // To populate form dropdowns
    collections: [], // To populate form dropdowns
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchProducts(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/products', { params });
        this.products = response.data;
      } catch (error) {
        this.error = 'Failed to fetch products.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchProduct(productId) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get(`/products/${productId}`);
        this.product = response.data;
        return this.product;
      } catch (error) {
        this.error = `Failed to fetch product ${productId}.`;
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    // Fetch categories and collections for the product form
    async fetchFormData() {
        this.isLoading = true;
        try {
            const [categoriesRes, collectionsRes] = await Promise.all([
                apiClient.get('/product-categories'),
                apiClient.get('/product-collections')
            ]);
            this.categories = categoriesRes.data;
            this.collections = collectionsRes.data;
        } catch (error) {
            this.error = 'Failed to fetch form data (categories/collections).';
            console.error(this.error, error);
        } finally {
            this.isLoading = false;
        }
    },

    async createProduct(productData) {
      this.isLoading = true;
      this.error = null;
      try {
        // The API might expect a FormData if images are included
        const formData = new FormData();
        for (const key in productData) {
            if (key === 'images' && productData[key]) {
                 for(let i = 0; i < productData[key].length; i++) {
                    formData.append('images', productData[key][i]);
                 }
            } else if (productData[key] !== null) {
                formData.append(key, productData[key]);
            }
        }
        await apiClient.post('/products', formData, {
             headers: { 'Content-Type': 'multipart/form-data' }
        });
        await this.fetchProducts();
      } catch (error) {
        this.error = 'Failed to create product.';
        console.error(this.error, error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async updateProduct(productId, productData) {
      this.isLoading = true;
      this.error = null;
      try {
        // Similar to create, handle FormData for updates if necessary
        const formData = new FormData();
        for (const key in productData) {
            if (key === 'images' && productData[key] && productData[key].length > 0) {
                 for(let i = 0; i < productData[key].length; i++) {
                    // Check if it's a new file or an existing image URL
                    if(productData[key][i] instanceof File) {
                        formData.append('images', productData[key][i]);
                    }
                 }
            } else if (productData[key] !== null) {
                formData.append(key, productData[key]);
            }
        }
        await apiClient.put(`/products/${productId}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        await this.fetchProducts();
      } catch (error) {
        this.error = 'Failed to update product.';
        console.error(this.error, error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async softDeleteProduct(productId) {
      this.isLoading = true;
      this.error = null;
      try {
        await apiClient.delete(`/products/${productId}`);
        await this.fetchProducts();
      } catch (error) {
        this.error = 'Failed to delete product.';
        console.error(this.error, error);
      } finally {
        this.isLoading = false;
      }
    },

    async hardDeleteProduct(productId) {
        this.isLoading = true;
        this.error = null;
        try {
          await apiClient.delete(`/products/${productId}?hard=true`);
          await this.fetchProducts();
        } catch (error) {
          this.error = 'Failed to permanently delete product.';
          console.error(this.error, error);
        } finally {
          this.isLoading = false;
        }
      },
  
      async restoreProduct(productId) {
        this.isLoading = true;
        this.error = null;
        try {
          await apiClient.put(`/products/${productId}/restore`);
          await this.fetchProducts();
        } catch (error) {
          this.error = 'Failed to restore product.';
          console.error(this.error, error);
        } finally {
          this.isLoading = false;
        }
      },
  },
});
