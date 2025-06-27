<template>
  <div class="bg-gray-50">
    <div class="mx-auto max-w-2xl px-4 pt-16 pb-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="sr-only">Checkout</h2>

      <div class="lg:grid lg:grid-cols-2 lg:gap-x-12 xl:gap-x-16">
        <div class="space-y-6">

          <!-- Step 1: Contact Information -->
          <CheckoutAccordionSection
            :step-number="1"
            title="Contact Information"
            :is-active="checkoutStore.activeSection === 'contact'"
            :is-complete="checkoutStore.isContactComplete"
            @activate="checkoutStore.setActiveSection('contact')"
          >
             <template #summary v-if="userStore.isLoggedIn">
                <p>Logged in as <span class="font-medium text-gray-900">{{ userStore.profile.email }}</span></p>
            </template>
            <div v-if="!userStore.isLoggedIn">
               <GuestCheckoutForm v-if="checkoutStore.isGuestMode" @completed="checkoutStore.setGuestDetails($event)"/>
               <div v-else>
                 <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
                    <button @click="checkoutStore.setGuestMode(true)" type="button" class="btn-primary w-full">Continue as Guest</button>
                    <button @click="showLogin = true" type="button" class="btn-secondary w-full">Log In</button>
                 </div>
                 <div v-if="showLogin" class="mt-8 border-t border-gray-200 pt-8">
                    <LoginForm @success="onLoginSuccess" />
                 </div>
               </div>
            </div>
          </CheckoutAccordionSection>

          <!-- Step 2: Shipping Information -->
          <CheckoutAccordionSection
            :step-number="2"
            title="Shipping Information"
            :is-active="checkoutStore.activeSection === 'shipping'"
            :is-complete="checkoutStore.isShippingComplete"
            @activate="checkoutStore.setActiveSection('shipping')"
          >
            <template #summary v-if="checkoutStore.shippingAddress">
                <p>{{ checkoutStore.shippingAddress.street }}, {{ checkoutStore.shippingAddress.city }}, {{ checkoutStore.shippingAddress.postal_code }}</p>
            </template>
            <AddressSelector @address-selected="checkoutStore.setShippingAddress($event)" />
          </CheckoutAccordionSection>

          <!-- Step 3: Delivery Method -->
          <CheckoutAccordionSection
            :step-number="3"
            title="Delivery Method"
            :is-active="checkoutStore.activeSection === 'delivery'"
            :is-complete="checkoutStore.isDeliveryComplete"
            @activate="checkoutStore.setActiveSection('delivery')"
          >
             <template #summary v-if="checkoutStore.deliveryMethod">
                <p>{{ checkoutStore.deliveryMethod.name }} - €{{ checkoutStore.deliveryMethod.price.toFixed(2) }}</p>
            </template>
            <DeliveryMethodSelector @method-selected="checkoutStore.setDeliveryMethod($event)" />
          </CheckoutAccordionSection>

          <!-- Step 4: Payment -->
          <CheckoutAccordionSection
            :step-number="4"
            title="Payment"
            :is-active="checkoutStore.activeSection === 'payment'"
            :is-complete="false" 
            @activate="checkoutStore.setActiveSection('payment')"
          >
            <p class="text-gray-600">Please review your order summary and proceed to payment.</p>
            <!-- Payment Gateway Component would go here -->
          </CheckoutAccordionSection>
        </div>

        <!-- Order summary (Right Column) -->
        <div class="mt-10 lg:mt-0">
          <OrderSummary />
          <div class="mt-6">
            <button 
              type="button" 
              class="w-full btn-primary" 
              @click="proceedToPayment"
              :disabled="checkoutStore.isSubmitting || !checkoutStore.isDeliveryComplete"
            >
              <span v-if="checkoutStore.isSubmitting">Placing Order...</span>
              <span v-else>Proceed to Payment</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../js/stores/user';
import { useCheckoutStore } from '../../js/stores/checkout';
import GuestCheckoutForm from '../components/checkout/GuestCheckoutForm.vue';
import AddressSelector from '../components/checkout/AddressSelector.vue';
import DeliveryMethodSelector from '../components/checkout/DeliveryMethodSelector.vue';
import OrderSummary from '../components/checkout/OrderSummary.vue';
import LoginForm from '../components/checkout/LoginForm.vue';
import CheckoutAccordionSection from '../components/checkout/CheckoutAccordionSection.vue';

const userStore = useUserStore();
const checkoutStore = useCheckoutStore();
const showLogin = ref(false);

function onLoginSuccess() {
    showLogin.value = false;
    checkoutStore.activeSection = 'shipping'; // Move to next step
}

function proceedToPayment() {
    checkoutStore.submitOrder();
}
</script>
