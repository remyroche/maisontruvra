import { defineStore } from 'pinia';
import { ref } from 'vue';
import { adminApiClient } from '@/services/api';
import { useNotificationStore } from './notification';
import api from '@/services/api';

export const useAdminProductsStore = defineStore('adminProducts', () => {
  const products = ref([]);

  async function fetchProducts(params) {
    try {
        const response = await api.adminGetProducts(params);
        products.value = response.data;
    } catch (error) {
        console.error("Failed to fetch products:", error);
    }
  }

  async function createProduct(productData) {
     try {
        await api.adminCreateProduct(productData);
        // Refresh the product list after creating
        await fetchProducts();
     } catch (error) {
        console.error("Failed to create product:", error);
        // Rethrow to let the component know the save failed
        throw error;
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
