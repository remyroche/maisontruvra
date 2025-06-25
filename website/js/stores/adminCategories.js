import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminCategoriesStore = defineStore('adminCategories', {
  state: () => ({
    categories: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCategories() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/product-categories');
        this.categories = response.data;
      } catch (e) {
        this.error = 'Failed to fetch product categories.';
      } finally {
        this.isLoading = false;
      }
    },
    async createCategory(categoryData) {
        try {
            await apiClient.post('/product-categories', categoryData);
            await this.fetchCategories();
        } catch (e) {
            this.error = 'Failed to create product category.';
            throw e;
        }
    },
    async updateCategory(id, categoryData) {
        try {
            await apiClient.put(`/product-categories/${id}`, categoryData);
            await this.fetchCategories();
        } catch (e) {
            this.error = 'Failed to update product category.';
            throw e;
        }
    },
    async deleteCategory(id) {
        try {
            await apiClient.delete(`/product-categories/${id}`);
            await this.fetchCategories();
        } catch (e) {
            this.error = 'Failed to delete product category.';
        }
    },
  },
});

