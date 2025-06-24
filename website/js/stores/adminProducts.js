/*
 * FILENAME: website/js/stores/adminProducts.js
 * DESCRIPTION: Pinia store for managing product data in the Admin Portal.
 *
 * This store handles the state and CRUD operations for products, including
 * fetching product lists, categories, and handling creation, updates, and deletion.
 * It follows the same robust error and loading state management pattern.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminProductStore = defineStore('adminProducts', () => {
  // --- STATE ---
  const products = ref([]);
  const categories = ref([]); // To populate form dropdowns
  const collections = ref([]); // To populate form dropdowns
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---

  /**
   * Fetches all necessary data for the product management page.
   */
  async function fetchProductsAndRelatedData() {
    isLoading.value = true;
    error.value = null;
    try {
      // Fetch products, categories, and collections in parallel
      const [productsRes, categoriesRes, collectionsRes] = await Promise.all([
        adminApiClient.get('/product-management/products'),
        adminApiClient.get('/product-management/categories'),
        adminApiClient.get('/product-management/collections')
      ]);
      products.value = productsRes.data.products;
      categories.value = categoriesRes.data.categories;
      collections.value = collectionsRes.data.collections;
    } catch (err) {
      console.error('Failed to fetch product data:', err);
      error.value = 'An error occurred while fetching product data.';
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Creates a new product.
   * @param {object} productData - The new product's data from the form.
   */
  async function createProduct(productData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.post('/product-management/products', productData);
      products.value.unshift(response.data.product);
       // --- LOGGING ---
      // The backend POST endpoint should trigger the AuditLogService for 'product_create'.
      return true;
    } catch (err) {
      console.error('Failed to create product:', err);
      error.value = `Failed to create product: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Updates an existing product.
   * @param {number} productId - The ID of the product to update.
   * @param {object} productData - The updated data.
   */
  async function updateProduct(productId, productData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await adminApiClient.put(`/product-management/products/${productId}`, productData);
      const index = products.value.findIndex(p => p.id === productId);
      if (index !== -1) {
        products.value[index] = response.data.product;
      }
      // --- LOGGING ---
      // The backend PUT endpoint should trigger the AuditLogService for 'product_update'.
      return true;
    } catch (err) {
      console.error(`Failed to update product ${productId}:`, err);
      error.value = `Failed to update product: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Deletes a product.
   * @param {number} productId - The ID of the product to delete.
   */
  async function deleteProduct(productId) {
    isLoading.value = true;
    error.value = null;
    try {
      await adminApiClient.delete(`/product-management/products/${productId}`);
      products.value = products.value.filter(p => p.id !== productId);
      // --- LOGGING ---
      // The backend DELETE endpoint should trigger the AuditLogService for 'product_delete'.
      return true;
    } catch (err) {
      console.error(`Failed to delete product ${productId}:`, err);
      error.value = `Failed to delete product: ${err.response?.data?.message || 'Server error'}`;
      return false;
    } finally {
      isLoading.value = false;
    }
  }


  return {
    products,
    categories,
    collections,
    isLoading,
    error,
    fetchProductsAndRelatedData,
    createProduct,
    updateProduct,
    deleteProduct,
  };
  
});
