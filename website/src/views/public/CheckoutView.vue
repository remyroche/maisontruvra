<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Finaliser ma commande</h1>
        <p class="mt-2 text-gray-600">Quelques étapes simples pour recevoir vos truffes d'exception</p>
      </div>

      <div class="mb-8">
        <nav aria-label="Progress">
          <ol class="flex items-center justify-center space-x-4 md:space-x-8">
            <li class="flex items-center">
              <div class="flex items-center">
                <div 
                  class="flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium"
                  :class="getStepClasses('contact')"
                >
                  <svg v-if="checkoutStore.isContactComplete" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span v-else>1</span>
                </div>
                <span class="ml-2 text-sm font-medium" :class="getStepTextClasses('contact')">Contact</span>
              </div>
            </li>
            </ol>
        </nav>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-6">
          <div v-if="checkoutStore.activeSection === 'contact'">
            </div>
          
          <div v-if="checkoutStore.activeSection === 'shipping'">
            </div>
          
          <div v-if="checkoutStore.activeSection === 'delivery'">
            </div>

          <div v-if="checkoutStore.activeSection === 'payment'" class="bg-white rounded-lg shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Paiement</h3>
            
            <PaymentForm @payment-token-generated="handlePaymentToken" />

            <div class="flex justify-between mt-6">
              <button @click="checkoutStore.setActiveSection('delivery')" class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">Retour</button>
              <button @click="handleSubmitOrder" :disabled="checkoutStore.isSubmitting" class="bg-brand-burgundy text-white px-8 py-3 rounded-md font-medium hover:bg-opacity-90 disabled:opacity-50">
                {{ checkoutStore.isSubmitting ? 'Traitement...' : 'Finaliser la commande' }}
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-1">
          <div class="sticky top-8">
            <OrderSummary :delivery-method="checkoutStore.deliveryMethod" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCheckoutStore } from '@/stores/checkout';
import { useUserStore } from '@/stores/user';
import { useCartStore } from '@/stores/cart';
import AddressSelector from '@/components/checkout/AddressSelector.vue';
import DeliveryMethodSelector from '@/components/checkout/DeliveryMethodSelector.vue';
import OrderSummary from '@/components/checkout/OrderSummary.vue';
import GuestCheckoutForm from '@/components/checkout/GuestCheckoutForm.vue';
import LoginForm from '@/components/checkout/LoginForm.vue';
import PaymentForm from '@/components/checkout/PaymentForm.vue';

const router = useRouter();
const checkoutStore = useCheckoutStore();
const userStore = useUserStore();
const cartStore = useCartStore();

const paymentToken = ref(null);

// --- Step Styling Logic (from your provided code) ---
const getStepClasses = (step) => { /* ... */ };
const getStepTextClasses = (step) => { /* ... */ };
const getStepComplete = (step) => { /* ... */ };

// --- Event Handlers to update the store ---
const handleLoginSuccess = () => checkoutStore.setUserMode();
const handleSwitchToGuest = () => checkoutStore.setGuestMode(true);
const handleGuestInfoSubmitted = (guestData) => checkoutStore.setGuestDetails(guestData);
const handleAddressSelected = (address) => checkoutStore.setShippingAddress(address);
const handleDeliveryMethodSelected = (method) => checkoutStore.setDeliveryMethod(method);
const handlePaymentToken = (token) => {
  paymentToken.value = token;
};

// --- Main Checkout Submission Logic ---
async function handleSubmitOrder() {
  if (!paymentToken.value) {
    alert("Payment details are not complete.");
    return;
  }

  // Construct the payload from the store's state
  const payload = {
    cart_id: cartStore.cart.id,
    payment_token: paymentToken.value,
  };

  if (checkoutStore.isGuestMode) {
    payload.guest_info = {
      email: checkoutStore.guestEmail,
      shipping_address: checkoutStore.shippingAddress,
      billing_address: checkoutStore.billingAddress || checkoutStore.shippingAddress
    };
  } else {
    payload.shipping_address_id = checkoutStore.shippingAddress.id;
    if (checkoutStore.billingAddress) {
      payload.billing_address_id = checkoutStore.billingAddress.id;
    }
  }

  // Call the store action to process the checkout
  try {
    const order = await checkoutStore.processCheckout(payload);
    router.push({ name: 'OrderConfirmation', params: { orderId: order.id } });
  } catch (error) {
    console.error('Order submission failed:', error);
    // You would show a user-friendly error notification here
  }
}

onMounted(() => {
  // Initial setup from your provided code
  if (!cartStore.cart || cartStore.cart.items.length === 0) {
    router.push({ name: 'Shop' });
  }
});
</script>
