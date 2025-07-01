<template>
  <form @submit.prevent="submitGuestCheckout">
    <div class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
        <input type="email" id="email" v-model="form.email" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-burgundy focus:border-brand-burgundy">
      </div>

      <h3 class="text-lg font-semibold pt-4">Shipping Address</h3>
      <AddressForm v-model="form.shipping_address" />

      <!-- You could add a checkbox here to use a different billing address -->

      <h3 class="text-lg font-semibold pt-4">Payment Details</h3>
      <div class="p-4 border rounded-md bg-gray-50">
        <!-- This would be replaced by a real payment element like Stripe Elements -->
        <label for="payment-token" class="block text-sm font-medium text-gray-700">Mock Payment Token</label>
        <input type="text" id="payment-token" v-model="form.payment_token" required placeholder="tok_mock_payment" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>
    </div>
    
    <button type="submit" class="mt-6 w-full bg-brand-burgundy text-white py-3 px-4 rounded-md hover:bg-opacity-90 transition-colors">
      Place Order
    </button>
  </form>
</template>

<script setup>
import { reactive } from 'vue';
import AddressForm from '@/components/forms/AddressForm.vue';

const emit = defineEmits(['guest-checkout-submit']);

const form = reactive({
  email: '',
  shipping_address: {
    first_name: '',
    last_name: '',
    address_line_1: '',
    city: '',
    postal_code: '',
    country: 'France'
  },
  payment_token: 'tok_mock_success' // Default mock token
});

const submitGuestCheckout = () => {
  emit('guest-checkout-submit', form);
};
</script>
