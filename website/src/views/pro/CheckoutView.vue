<template>
  <div class="bg-gray-100">
    <div class="container mx-auto py-12 px-4">
      <h1 class="text-3xl font-bold text-center mb-8">Professional Checkout</h1>

      <div v-if="profileLoading || cartLoading" class="text-center py-20">
        <p>Loading checkout details...</p>
      </div>
      <div v-else-if="profileError || cartError" class="text-center py-20 text-red-600">
        <p>Could not load checkout details. Please ensure you are logged in and try again.</p>
      </div>
      <div v-else-if="profile && cart" class="grid grid-cols-1 lg:grid-cols-3 gap-12">

        <!-- Checkout Form -->
        <form @submit.prevent="handleCheckout" id="checkout-form" class="lg:col-span-2 space-y-8">
          <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-4">Shipping Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="company" class="block text-sm font-medium text-gray-700">Company</label>
                <input type="text" id="company" v-model="form.companyName" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" readonly>
              </div>
              <div>
                <label for="vat" class="block text-sm font-medium text-gray-700">VAT Number</label>
                <input type="text" id="vat" v-model="form.vatNumber" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" readonly>
              </div>
              <div class="md:col-span-2">
                <label for="address" class="block text-sm font-medium text-gray-700">Shipping Address</label>
                <input type="text" id="address" v-model="form.address" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" required>
              </div>
            </div>
          </div>

          <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-4">Payment Method</h2>
            <p class="text-gray-600">Payment processing is handled via invoice after order placement. No payment is required at this time.</p>
          </div>
        </form>

        <!-- Order Summary -->
        <div class="lg:col-span-1">
          <div class="bg-white p-6 rounded-lg shadow sticky top-8">
            <h2 class="text-xl font-semibold mb-4 border-b pb-4">Order Summary</h2>
            <div v-if="cart.items.length > 0" class="space-y-2">
              <div v-for="item in cart.items" :key="item.id" class="flex justify-between text-sm">
                <span class="truncate pr-2">{{ item.quantity }} x {{ item.name }}</span>
                <span class="font-medium whitespace-nowrap">€{{ (item.price * item.quantity).toFixed(2) }}</span>
              </div>
            </div>
            <div v-else>
                <p class="text-sm text-gray-500">Your cart is empty.</p>
            </div>
            <div class="border-t pt-4 mt-4 space-y-1">
              <div class="flex justify-between font-semibold">
                <span>Subtotal (HT)</span>
                <span>€{{ cart.subtotal.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-sm text-gray-600">
                <span>VAT (20% estimate)</span>
                <span>€{{ cart.vat.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-bold text-lg mt-2 border-t pt-2">
                <span>Total (TTC)</span>
                <span>€{{ cart.total.toFixed(2) }}</span>
              </div>
            </div>
            <button type="submit" form="checkout-form" :disabled="isSubmitting || cart.items.length === 0" class="w-full bg-black text-white font-bold py-3 px-8 rounded-md hover:bg-gray-800 transition-colors mt-6 disabled:bg-gray-400">
              {{ isSubmitting ? 'Placing Order...' : 'Place Order' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api';

const router = useRouter();
const isSubmitting = ref(false);

const { data: profile, isLoading: profileLoading, error: profileError } = useApiData(() => apiClient.get('/b2b/profile'));
const { data: cart, isLoading: cartLoading, error: cartError } = useApiData(() => apiClient.get('/b2b/profile/cart'));

const form = reactive({
  companyName: '',
  vatNumber: '',
  address: '',
});

watch(profile, (newProfile) => {
  if (newProfile) {
    form.companyName = newProfile.company_name;
    form.vatNumber = newProfile.vat_number;
    form.address = newProfile.default_shipping_address || '';
  }
});

const handleCheckout = async () => {
  if (cart.value.items.length === 0) return;
  isSubmitting.value = true;
  try {
    const orderPayload = {
      shipping_address: form.address,
      // The backend will use the cart from the user's session
    };
    const response = await apiClient.post('/b2b/profile/orders/create', orderPayload);
    // On success, redirect to a confirmation page
    router.push({ name: 'ProOrderConfirmation', params: { orderId: response.order_id } });
  } catch (err) {
    console.error('Checkout failed', err);
    // The API client interceptor will show a notification
  } finally {
    isSubmitting.value = false;
  }
};
</script>