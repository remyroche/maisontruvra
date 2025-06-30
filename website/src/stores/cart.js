import { defineStore } from 'pinia';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
  }),
  
  // Recommendation Implemented: Added getters for derived state.
  // This centralizes the logic for calculating cart properties like item count
  // and the total price, ensuring it's consistent wherever it's used in the app.
  getters: {
    /**
     * Calculates the total number of items in the cart.
     * @returns {number} The total item count.
     */
    itemCount: (state) => {
      return state.items.reduce((total, item) => total + item.quantity, 0);
    },

    /**
     * Calculates the total price of all items in the cart.
     * @returns {number} The total price of the cart.
     */
    totalPrice: (state) => {
      return state.items.reduce((total, item) => total + (item.product.price * item.quantity), 0);
    },
  },

  actions: {
    async fetchCart() {
      this.loading = true;
      try {
        const response = await api.get('/cart');
        this.items = response.data.items;
      } catch (error) {
        this.error = 'Failed to fetch cart.';
        const notificationStore = useNotificationStore();
        notificationStore.addNotification('Error fetching cart', 'error');
      } finally {
        this.loading = false;
      }
    },

    async addToCart(productId, quantity) {
      this.loading = true;
      const notificationStore = useNotificationStore();
      try {
        await api.post('/cart/add', { product_id: productId, quantity });
        await this.fetchCart(); // Refresh cart state
        notificationStore.addNotification('Item added to cart', 'success');
      } catch (error) {
        this.error = 'Failed to add item to cart.';
        notificationStore.addNotification('Could not add item to cart', 'error');
      } finally {
        this.loading = false;
      }
    },

    async removeFromCart(itemId) {
        this.loading = true;
        const notificationStore = useNotificationStore();
        try {
            await api.post('/cart/remove', { item_id: itemId });
            await this.fetchCart(); // Refresh cart state
            notificationStore.addNotification('Item removed from cart', 'success');
        } catch (error) {
            this.error = 'Failed to remove item from cart.';
            notificationStore.addNotification('Could not remove item from cart', 'error');
        } finally {
            this.loading = false;
        }
    },

    async updateQuantity(itemId, quantity) {
        if (quantity <= 0) {
            await this.removeFromCart(itemId);
            return;
        }
        this.loading = true;
        const notificationStore = useNotificationStore();
        try {
            await api.post('/cart/update', { item_id: itemId, quantity });
            await this.fetchCart(); // Refresh cart state
            notificationStore.addNotification('Cart updated', 'success');
        } catch (error) {
            this.error = 'Failed to update cart quantity.';
            notificationStore.addNotification('Could not update cart', 'error');
        } finally {
            this.loading = false;
        }
    },

    clearCart() {
      this.items = [];
      // Optionally, could also call an API endpoint to clear the cart on the server
    }
  },
});
