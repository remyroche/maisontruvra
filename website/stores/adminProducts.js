import { defineStore } from 'pinia';
import { ref } from 'vue';
import { adminApiClient } from '@/services/api';
import { useNotificationStore } from './notification';

export const useAdminProductsStore = defineStore('adminProducts', () => {
  const products = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  const notificationStore = useNotificationStore();

  // Although the main view uses useApiData, this action can be useful for other components or for programmatic refreshes.
  async function fetchProducts(options = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const params = new URLSearchParams(options);
      const data = await adminApiClient.get(`/products?${params.toString()}`);
      products.value = data.data; // Assuming paginated response
      return data;
    } catch (e) {
      error.value = 'Failed to fetch products.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  async function _handleAction(actionPromise, successMessage) {
    try {
      await actionPromise;
      notificationStore.showNotification({ message: successMessage, type: 'success' });
      return true;
    } catch (e) {
      // Error is handled by the global API interceptor
      console.error(e);
      return false;
    }
  }

  function createProduct(productData) {
    return _handleAction(
      adminApiClient.post('/products', productData),
      'Product created successfully.'
    );
  }

  function updateProduct(productId, productData) {
    return _handleAction(
      adminApiClient.put(`/products/${productId}`, productData),
      'Product updated successfully.'
    );
  }

  function softDeleteProduct(productId) {
    return _handleAction(
      adminApiClient.delete(`/products/${productId}`),
      'Product moved to trash.'
    );
  }

  function hardDeleteProduct(productId) {
    return _handleAction(
      adminApiClient.delete(`/products/${productId}?hard=true`),
      'Product permanently deleted.'
    );
  }

  function restoreProduct(productId) {
    return _handleAction(
      adminApiClient.put(`/products/${productId}/restore`),
      'Product restored successfully.'
    );
  }

  return {
    products,
    isLoading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    softDeleteProduct,
    hardDeleteProduct,
    restoreProduct,
  };
});
