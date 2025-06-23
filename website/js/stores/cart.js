import { defineStore } from 'pinia';
import { apiClient } from '../api-client.js';

// This is a global cart store that can be used by both B2C and B2B shops
export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    itemCount: 0,
    subtotal: 0,
    isLoaded: false,
  }),
  getters: {
    formattedSubtotal: (state) => {
        return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(state.subtotal || 0);
    }
  },
  actions: {
    _updateCartState(cartData) {
        this.items = cartData.items;
        this.itemCount = cartData.item_count;
        this.subtotal = cartData.subtotal;
        this.isLoaded = true;
    },
    async fetchCart() {
      if (this.isLoaded) return;
      try {
        const response = await apiClient.get('/api/cart');
        this._updateCartState(response.data);
      } catch (error) {
        console.error('Failed to fetch cart:', error);
        this.isLoaded = true;
      }
    },
    async addItem(productId, quantity) {
      try {
        const response = await apiClient.post('/api/cart/add', { product_id: productId, quantity });
        this._updateCartState(response.data.cart);
      } catch (error) {
        console.error('Failed to add item to cart:', error);
      }
    },
    async updateItem(itemId, quantity) {
        try {
            const response = await apiClient.put(`/api/cart/item/${itemId}`, { quantity });
            this._updateCartState(response.data.cart);
        } catch (error) { console.error('Failed to update item:', error); }
    },
    async removeItem(itemId) {
        try {
            const response = await apiClient.delete(`/api/cart/item/${itemId}`);
            this._updateCartState(response.data.cart);
        } catch (error) { console.error('Failed to remove item:', error); }
    },
    async addMultipleItems(items) {
      try {
        const response = await apiClient.post('/api/cart/add-multiple', { items });
        this._updateCartState(response.data.cart);
      } catch (error) {
        console.error('Failed to add multiple items:', error);
      }
    }
  },
});
