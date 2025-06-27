import { defineStore } from 'pinia';
import { useCartStore } from './cart';
import { useUserStore } from './user';
import { useNotificationStore } from './notification';
import { apiClient } from '../api-client';

export const useCheckoutStore = defineStore('checkout', {
  state: () => ({
    isGuestMode: false,
    guestDetails: { email: '', first_name: '', last_name: '' },
    shippingAddress: null,
    deliveryMethod: null,
    isSubmitting: false,
  }),
  actions: {
    setGuestMode(value) {
      this.isGuestMode = value;
    },
    
    // ... other setters for address, delivery method ...

    async submitOrder() {
      const cartStore = useCartStore();
      const userStore = useUserStore();
      const notificationStore = useNotificationStore();

      if (cartStore.isEmpty) {
        notificationStore.showNotification({ message: "Your cart is empty.", type: 'error' });
        return;
      }
      // Add more validation checks here (e.g., address selected)

      this.isSubmitting = true;
      try {
        const payload = {
            cart_id: cartStore.cartId,
            shipping_address_id: this.shippingAddress.id,
            // ... add other necessary data like delivery method id
        };

        // Add guest details if applicable
        if (this.isGuestMode && !userStore.isLoggedIn) {
            payload.guest_details = this.guestDetails;
        }

        const response = await apiClient.post('/orders/create', payload);
        
        // Order successful
        notificationStore.showNotification({ message: "Your order has been placed successfully!", type: 'success' });
        cartStore.clearCart(); // Clear the local cart state
        
        // Redirect to an order confirmation page
        // router.push({ name: 'OrderConfirmation', params: { orderId: response.data.id } });

      } catch (error) {
        const errorMessage = error.response?.data?.error || "Could not place your order. Please try again.";
        notificationStore.showNotification({ message: errorMessage, type: 'error' });
      } finally {
        this.isSubmitting = false;
      }
    }
  },
});
