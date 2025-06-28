import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';

export const useCartStore = defineStore('cart', () => {
  const cart = ref(null);
  const isLoading = ref(false);

  const itemCount = computed(() => {
    if (!cart.value || !cart.value.items) return 0;
    return cart.value.items.reduce((total, item) => total + item.quantity, 0);
  });

  async function fetchCart() {
    isLoading.value = true;
    try {
      cart.value = await apiClient.get('/cart');
    } catch (error) {
      console.error("Failed to fetch cart:", error);
      cart.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clears the cart from the local state.
   * This is typically called after a successful order placement.
   */
  function clearLocalCart() {
    cart.value = null;
  }

  async function addItem(productId, quantity = 1) {
    try {
      const updatedCart = await apiClient.post('/cart/items', {
        product_id: productId,
        quantity: quantity,
      });
      cart.value = updatedCart;
    } catch (error) {
      console.error("Failed to add item to cart:", error);
      // Error notification is handled by the API interceptor
    }
  }

  async function removeItem(itemId) {
    try {
      cart.value = await apiClient.delete(`/cart/items/${itemId}`);
    } catch (error) {
      console.error("Failed to remove item from cart:", error);
    }
  }

  async function updateItemQuantity(itemId, quantity) {
    try {
      cart.value = await apiClient.put(`/cart/items/${itemId}`, { quantity });
    } catch (error) {
      console.error("Failed to update item quantity:", error);
    }
  }

  return { cart, isLoading, itemCount, fetchCart, clearLocalCart, addItem, removeItem, updateItemQuantity };
});