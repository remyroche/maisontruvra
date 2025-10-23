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
        <!-- Stripe Elements integration -->
        <div id="card-element" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm p-3">
          <!-- Stripe Elements will create form elements here -->
        </div>
        <div id="card-errors" role="alert" class="text-red-600 text-sm mt-2"></div>
      </div>
    </div>
    
    <button type="submit" class="mt-6 w-full bg-brand-burgundy text-white py-3 px-4 rounded-md hover:bg-opacity-90 transition-colors">
      Place Order
    </button>
  </form>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import { loadStripe } from '@stripe/stripe-js';
import AddressForm from '@/components/forms/AddressForm.vue';

const emit = defineEmits(['guest-checkout-submit']);

// Stripe setup
let stripe = null;
let elements = null;
let cardElement = null;

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
  payment_token: null // Will be set by Stripe Elements
});

// Initialize Stripe
onMounted(async () => {
  try {
    stripe = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);
    if (stripe) {
      elements = stripe.elements();
      cardElement = elements.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#424770',
            '::placeholder': {
              color: '#aab7c4',
            },
          },
        },
      });
      cardElement.mount('#card-element');
      
      cardElement.on('change', ({error}) => {
        const displayError = document.getElementById('card-errors');
        if (error) {
          displayError.textContent = error.message;
        } else {
          displayError.textContent = '';
        }
      });
    }
  } catch (error) {
    console.error('Error loading Stripe:', error);
  }
});

const submitGuestCheckout = async () => {
  if (!stripe || !cardElement) {
    console.error('Stripe not loaded');
    return;
  }

  try {
    const {error, paymentMethod} = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
      billing_details: {
        email: form.email,
        name: `${form.shipping_address.first_name} ${form.shipping_address.last_name}`,
        address: {
          line1: form.shipping_address.address_line_1,
          city: form.shipping_address.city,
          postal_code: form.shipping_address.postal_code,
          country: form.shipping_address.country,
        },
      },
    });

    if (error) {
      console.error('Error creating payment method:', error);
      return;
    }

    form.payment_token = paymentMethod.id;
    emit('guest-checkout-submit', form);
  } catch (error) {
    console.error('Error processing payment:', error);
  }
};
</script>
