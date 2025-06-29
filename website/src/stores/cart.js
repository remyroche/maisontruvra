// website/src/stores/cart.js
// Description: This store is simplified to use the new API service methods.

import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api'; // Use the new centralized API service

export const useCartStore = defineStore('cart', () => {
  const items = ref([]);
  const cartId = ref(null);

  async function fetchCart() {
    try {
      const response = await api.getCart();
      items.value = response.data.items;
      cartId.value = response.data.id;
    } catch (error) {
      console.error('Failed to fetch cart:', error);
      // No user notification needed here, the interceptor does it.
    }
  }

  // The addItem action now calls the dedicated API method.
  async function addItem(productId, quantity = 1) {
    try {
      const response = await api.addToCart(productId, quantity);
      // On success, update the cart state from the response
      items.value = response.data.items;
    } catch (error) {
      // The error is already handled and shown to the user by the api.js interceptor.
      console.error('Failed to add item to cart:', error);
    }
  }

  // ... other actions (removeItem, updateQuantity) would be simplified similarly ...
  async function removeItem(itemId) {
    try {
        const response = await api.removeFromCart(itemId);
        items.value = response.data.items;
    } catch(error) {
        console.error('Failed to remove item from cart:', error);
    }
  }


  return { items, addItem, fetchCart, removeItem };
});