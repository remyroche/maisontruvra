import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { useCartStore } from './cart';
import { useUserStore } from './user';

export const useCheckoutStore = defineStore('checkout', () => {
  const router = useRouter();
  const cartStore = useCartStore();
  const userStore = useUserStore();

  // State for managing the multi-step UI
  const activeSection = ref('contact'); // contact, shipping, delivery, payment
  const isGuestMode = ref(false);
  const isSubmitting = ref(false);

  // State for holding checkout data
  const guestEmail = ref('');
  const shippingAddress = ref(null);
  const billingAddress = ref(null);
  const deliveryMethod = ref(null);
  const paymentToken = ref(null); // To hold the token from the payment provider

  // --- Computed properties for progress bar ---
  const isContactComplete = computed(() => {
    return (userStore.isLoggedIn && !isGuestMode.value) || (isGuestMode.value && guestEmail.value);
  });
  const isShippingComplete = computed(() => !!shippingAddress.value);
  const isDeliveryComplete = computed(() => !!deliveryMethod.value);

  // --- Actions to update state from the UI ---
  function setActiveSection(section) {
    activeSection.value = section;
  }

  function setGuestMode(mode) {
    isGuestMode.value = mode;
  }

  function setGuestDetails(details) {
    guestEmail.value = details.email;
    shippingAddress.value = details.shipping_address;
    billingAddress.value = details.billing_address || details.shipping_address;
    setActiveSection('delivery');
  }
  
  function setUserMode() {
    isGuestMode.value = false;
    setActiveSection('shipping');
  }

  function setShippingAddress(address) {
    shippingAddress.value = address;
    // If no separate billing address is set, use the shipping address
    if (!billingAddress.value) {
        billingAddress.value = address;
    }
    setActiveSection('delivery');
  }

  function setDeliveryMethod(method) {
    deliveryMethod.value = method;
    setActiveSection('payment');
  }
  
  function setPaymentToken(token) {
    paymentToken.value = token;
  }

  // --- Main Action to Submit the Order ---
  async function submitOrder() {
    if (!paymentToken.value) {
      console.error("Payment token is missing.");
      // You would typically show a user-facing error here
      return;
    }
    
    isSubmitting.value = true;
    try {
      // Build the payload based on the store's state
      const payload = {
        cart_id: cartStore.cart.id,
        payment_token: paymentToken.value,
      };

      if (isGuestMode.value) {
        payload.guest_info = {
          email: guestEmail.value,
          shipping_address: shippingAddress.value,
          billing_address: billingAddress.value,
        };
      } else {
        payload.shipping_address_id = shippingAddress.value.id;
        if (billingAddress.value && billingAddress.value.id !== shippingAddress.value.id) {
            payload.billing_address_id = billingAddress.value.id;
        }
      }

      const response = await api.post('/checkout/', payload);

      // On success, clear the local cart state and redirect.
      cartStore.clearCart();
      
      // Redirect to order confirmation page
      router.push({ 
        name: 'OrderConfirmation', 
        params: { orderId: response.data.order_id }
      });

    } catch (error) {
      // The API client interceptor can handle showing a generic error notification.
      console.error("Order submission failed:", error);
    } finally {
      isSubmitting.value = false;
    }
  }

  // Reset state when leaving checkout
  function resetCheckoutState() {
      activeSection.value = 'contact';
      isGuestMode.value = false;
      isSubmitting.value = false;
      guestEmail.value = '';
      shippingAddress.value = null;
      billingAddress.value = null;
      deliveryMethod.value = null;
      paymentToken.value = null;
  }

  return {
    activeSection,
    isContactComplete,
    isShippingComplete,
    isDeliveryComplete,
    isGuestMode,
    guestEmail,
    shippingAddress,
    deliveryMethod,
    isSubmitting,
    setActiveSection,
    setGuestDetails,
    setGuestMode,
    setUserMode,
    setShippingAddress,
    setDeliveryMethod,
    setPaymentToken,
    submitOrder,
    resetCheckoutState,
  };
});
