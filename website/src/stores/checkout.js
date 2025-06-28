import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { apiClient } from '@/services/api';
import { useCartStore } from './cart';

export const useCheckoutStore = defineStore('checkout', () => {
  const router = useRouter();
  const cartStore = useCartStore();

  const activeSection = ref('contact');
  const isContactComplete = ref(false);
  const isShippingComplete = ref(false);
  const isDeliveryComplete = ref(false);
  const isGuestMode = ref(false);
  const guestEmail = ref('');
  const shippingAddress = ref(null);
  const deliveryMethod = ref(null);
  const isSubmitting = ref(false);

  function setActiveSection(section) {
    activeSection.value = section;
  }

  function setGuestDetails(details) {
    guestEmail.value = details.email;
    isContactComplete.value = true;
    activeSection.value = 'shipping';
  }

  function setGuestMode(mode) {
    isGuestMode.value = mode;
  }

  function setShippingAddress(address) {
    shippingAddress.value = address;
    isShippingComplete.value = true;
    activeSection.value = 'delivery';
  }

  function setDeliveryMethod(method) {
    deliveryMethod.value = method;
    isDeliveryComplete.value = true;
    activeSection.value = 'payment';
  }

  async function submitOrder() {
    isSubmitting.value = true;
    try {
      const orderPayload = {
        shipping_address_id: shippingAddress.value.id,
        delivery_method_id: deliveryMethod.value.id,
      };

      if (isGuestMode.value && guestEmail.value) {
        orderPayload.guest_email = guestEmail.value;
      }

      const response = await apiClient.post('/orders/create', orderPayload);

      // On success, clear the local cart state and redirect.
      cartStore.clearLocalCart();
      
      // Redirect to order confirmation page
      router.push({ 
        name: 'OrderConfirmation', 
        params: { id: response.order.id },
        query: { order_number: response.order.order_number }
      });

    } catch (error) {
      // The API client interceptor will show an error notification.
      console.error("Order submission failed:", error);
    } finally {
      isSubmitting.value = false;
    }
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
    setShippingAddress,
    setDeliveryMethod,
    submitOrder,
  };
});