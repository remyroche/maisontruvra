import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useB2BShopStore } from './b2b-shop'; // Assumes a B2B cart store exists
import apiClient from '../api-client';

export const useB2BCheckoutStore = defineStore('b2bCheckout', () => {
  // --- STATE ---
  const deliveryMethods = ref([]);
  const selectedDeliveryMethod = ref(null);
  const loading = ref(false);
  const error = ref(null);

  // Assumes a B2B cart store is available to provide the subtotal
  const b2bShopStore = useB2BShopStore(); 

  // --- ACTIONS ---
  async function fetchDeliveryMethods() {
    loading.value = true;
    error.value = null;
    try {
      // apiClient will need a method to get B2B delivery options
      const methods = await apiClient.getB2BDeliveryMethods();
      deliveryMethods.value = methods.map(m => ({
        ...m,
        price: parseFloat(m.price),
        displayPrice: `${parseFloat(m.price).toFixed(2).replace('.', ',')} € HT`
      }));
      // Set a default delivery method
      if (deliveryMethods.value.length > 0) {
        selectedDeliveryMethod.value = deliveryMethods.value[0];
      }
    } catch (e) {
      console.error("Failed to fetch B2B delivery methods:", e);
      error.value = "Impossible de charger les options de livraison.";
    } finally {
      loading.value = false;
    }
  }

  // --- GETTERS ---
  const shippingCost = computed(() => {
    return selectedDeliveryMethod.value ? selectedDeliveryMethod.value.price : 0.00;
  });

  const subtotal = computed(() => {
    // Ensure subtotal from cart store is a number
    return parseFloat(b2bShopStore.subtotal) || 0;
  });

  // This is the total price *before* taxes (HT - Hors Taxes)
  const totalHT = computed(() => {
    return subtotal.value + shippingCost.value;
  });

  return {
    deliveryMethods,
    selectedDeliveryMethod,
    loading,
    error,
    shippingCost,
    subtotal,
    totalHT,
    fetchDeliveryMethods,
  };
});
