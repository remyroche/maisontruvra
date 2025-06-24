<template>
  <div class="bg-gray-50">
    <div class="mx-auto max-w-2xl px-4 pt-16 pb-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="sr-only">Checkout</h2>

      <div class="lg:grid lg:grid-cols-2 lg:gap-x-12 xl:gap-x-16">
        <div>
          <!-- Guest vs Login Selector -->
          <div v-if="!authStore.isAuthenticated && !checkoutStore.isGuestMode">
            <h2 class="text-lg font-medium text-gray-900">Informations de contact</h2>
            <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
               <button @click="checkoutStore.setGuestMode(true)" type="button" class="btn-primary w-full">Continuer en tant qu'invité</button>
               <button @click="showLogin = true" type="button" class="btn-secondary w-full">Se connecter</button>
            </div>
             <!-- Simple Login Form (could be a component) -->
            <div v-if="showLogin" class="mt-8 border-t border-gray-200 pt-8">
                <LoginForm @success="onLoginSuccess" />
            </div>
          </div>

          <!-- Guest Details Form -->
          <GuestCheckoutForm v-if="!authStore.isAuthenticated && checkoutStore.isGuestMode" />
          
          <!-- Authenticated User Address -->
          <AddressSelector v-if="authStore.isAuthenticated" />

          <!-- Delivery Methods -->
          <DeliveryMethodSelector class="mt-10 border-t border-gray-200 pt-10" />
        </div>

        <!-- Order summary -->
        <div class="mt-10 lg:mt-0">
          <OrderSummary />
          <div class="mt-6">
             <button type="submit" class="w-full btn-primary" @click="proceedToPayment">Procéder au paiement</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useCheckoutStore } from '../stores/checkout';
import GuestCheckoutForm from '../components/checkout/GuestCheckoutForm.vue';
import AddressSelector from '../components/checkout/AddressSelector.vue';
import DeliveryMethodSelector from '../components/checkout/DeliveryMethodSelector.vue';
import OrderSummary from '../components/checkout/OrderSummary.vue';
import LoginForm from '../components/checkout/LoginForm.vue';

const authStore = useAuthStore();
const checkoutStore = useCheckoutStore();
const showLogin = ref(false);

function onLoginSuccess() {
    showLogin.value = false;
    // The view will become reactive to the new auth state
}

function proceedToPayment() {
    // Logic to gather all data from stores and call the correct API endpoint
    // e.g., apiClient.createGuestOrder or apiClient.createAuthenticatedOrder
    alert('Proceeding to payment...');
}
</script>
