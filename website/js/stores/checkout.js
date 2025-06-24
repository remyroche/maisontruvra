import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useCheckoutStore = defineStore('checkout', () => {
  const checkoutStep = ref('information'); // 'information', 'delivery', 'payment'
  const isGuestMode = ref(false);
  
  const guestDetails = ref({
    email: '',
    phone: '',
  });

  const shippingAddress = ref({
    street: '',
    city: '',
    postal_code: '',
    country: 'FR',
  });
  
  const deliveryMethod = ref(null);

  function setGuestMode(isGuest) {
    isGuestMode.value = isGuest;
  }

  function setStep(step) {
    checkoutStep.value = step;
  }

  function reset() {
    checkoutStep.value = 'information';
    isGuestMode.value = false;
    guestDetails.value = { email: '', phone: '' };
    shippingAddress.value = { street: '', city: '', postal_code: '', country: 'FR' };
    deliveryMethod.value = null;
  }

  return {
    checkoutStep,
    isGuestMode,
    guestDetails,
    shippingAddress,
    deliveryMethod,
    setGuestMode,
    setStep,
    reset,
  };
});
