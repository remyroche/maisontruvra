/*
 * FILENAME: website/js/stores/adminCategories.js
 * DESCRIPTION: Pinia store for managing product category data in the Admin Portal.
 *
 * This store handles all state and CRUD operations for product categories.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminCategoryStore = defineStore('adminCategories', () => {
  // --- STATE ---
  const categories = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  async function fetchCategories() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.get('/product-management/categories');
      categories.value = response.data.categories;
    } catch (err) {
      console.error('Failed to fetch categories:', err);
      error.value = 'An error occurred while fetching categories.';
    } finally {
      isLoading.value = false;
    }
  }

  async function createCategory(categoryData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.post('/product-management/categories', categoryData);
      categories.value.unshift(response.data.category);
      // --- LOGGING ---
      // The backend POST endpoint should trigger AuditLogService for 'category_create'.
      return true;
    } catch (err) {
      console.error('Failed to create category:', err);
      error.value = `Failed to create category: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateCategory(categoryId, categoryData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/product-management/categories/${categoryId}`, categoryData);
      const index = categories.value.findIndex(c => c.id === categoryId);
      if (index !== -1) {
        categories.value[index] = response.data.category;
      }
      // --- LOGGING ---
      // The backend PUT endpoint should trigger AuditLogService for 'category_update'.
      return true;
    } catch (err) {
      console.error(`Failed to update category ${categoryId}:`, err);
      error.value = `Failed to update category: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteCategory(categoryId) {
    isLoading.value = true;
    error.value = null;
    try {
      await adminApiClient.delete(`/product-management/categories/${categoryId}`);
      categories.value = categories.value.filter(c => c.id !== categoryId);
       // --- LOGGING ---
      // The backend DELETE endpoint should trigger AuditLogService for 'category_delete'.
      return true;
    } catch (err) {
      console.error(`Failed to delete category ${categoryId}:`, err);
      error.value = `Failed to delete category: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    categories,
    isLoading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
  };
});
