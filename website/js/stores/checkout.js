import { defineStore } from 'pinia';
import { useCartStore } from './cart';
import { useUserStore } from './user';
import { useNotificationStore } from './notification';
import { apiClient } from '../api-client';

export const useCheckoutStore = defineStore('checkout', {
  state: () => ({
    // State for the accordion flow
    activeSection: 'contact', // Tracks the currently open section
    
    // Existing state
    isGuestMode: false,
    guestDetails: null, // Use null to easily check for completion
    shippingAddress: null,
    deliveryMethod: null,
    isSubmitting: false,
  }),
  
  getters: {
    // Getters to determine if a step is complete, which drives the UI state
    isContactComplete: (state) => {
        const userStore = useUserStore();
        return (state.guestDetails !== null && state.isGuestMode) || userStore.isLoggedIn;
    },
    isShippingComplete: (state) => state.shippingAddress !== null,
    isDeliveryComplete: (state) => state.deliveryMethod !== null,
  },

  actions: {
    setGuestMode(value) {
      this.isGuestMode = value;
      this.activeSection = 'contact';
    },

    // Actions to set data and automatically advance the accordion
    setGuestDetails(details) {
        this.guestDetails = details;
        this.activeSection = 'shipping';
    },
    
    setShippingAddress(address) {
        this.shippingAddress = address;
        this.activeSection = 'delivery';
    },
    
    setDeliveryMethod(method) {
        this.deliveryMethod = method;
        this.activeSection = 'payment';
    },
    
    // Allows the user to click on a previous, completed section to edit it
    setActiveSection(sectionName) {
      if (sectionName === 'contact' && this.isContactComplete) {
        this.activeSection = sectionName;
      } else if (sectionName === 'shipping' && this.isShippingComplete) {
        this.activeSection = sectionName;
      } else if (sectionName === 'delivery' && this.isDeliveryComplete) {
        this.activeSection = sectionName;
      }
    },

    // The final submission logic remains the same
    async submitOrder() {
      const cartStore = useCartStore();
      const userStore = useUserStore();
      const notificationStore = useNotificationStore();

      // More robust validation before submitting
      if (!this.isContactComplete || !this.isShippingComplete || !this.isDeliveryComplete) {
          notificationStore.showNotification({ message: "Please complete all steps before proceeding.", type: 'error' });
          return;
      }
      if (cartStore.isEmpty) {
        notificationStore.showNotification({ message: "Your cart is empty.", type: 'error' });
        return;
      }

      this.isSubmitting = true;
      try {
        const payload = {
            shipping_address_id: this.shippingAddress.id,
            delivery_method_id: this.deliveryMethod.id,
            // The backend will use the authenticated user's cart
        };

        if (this.isGuestMode && !userStore.isLoggedIn) {
            payload.guest_details = this.guestDetails;
        }

        const response = await apiClient.post('/orders/create', payload);
        
        notificationStore.showNotification({ message: "Your order has been placed successfully!", type: 'success' });
        cartStore.clearCart(); 
        
        // Reset checkout state and redirect
        this.$reset();
        // Example: router.push({ name: 'OrderConfirmation', params: { orderId: response.data.id } });

      } catch (error) {
        const errorMessage = error.response?.data?.error || "Could not place your order. Please try again.";
        notificationStore.showNotification({ message: errorMessage, type: 'error' });
      } finally {
        this.isSubmitting = false;
      }
    },

    // Action to reset the store to its initial state
    $reset() {
        this.activeSection = 'contact';
        this.isGuestMode = false;
        this.guestDetails = null;
        this.shippingAddress = null;
        this.deliveryMethod = null;
        this.isSubmitting = false;
    }
  },
});
