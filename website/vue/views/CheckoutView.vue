<template>
  <div class="bg-gray-50">
    <div class="mx-auto max-w-2xl px-4 pt-16 pb-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="sr-only">Checkout</h2>

      <div class="lg:grid lg:grid-cols-2 lg:gap-x-12 xl:gap-x-16">
        <div>
          <!-- Guest vs Login Selector -->
          <div v-if="!userStore.isLoggedIn && !checkoutStore.isGuestMode">
            <h2 class="text-lg font-medium text-gray-900">Contact Information</h2>
            <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
                <button @click="checkoutStore.setGuestMode(true)" type="button" class="btn-primary w-full">Continue as Guest</button>
                <button @click="showLogin = true" type="button" class="btn-secondary w-full">Log In</button>
            </div>
            <!-- Simple Login Form -->
            <div v-if="showLogin" class="mt-8 border-t border-gray-200 pt-8">
                <LoginForm @success="onLoginSuccess" />
            </div>
          </div>

          <!-- Guest Details Form -->
          <GuestCheckoutForm v-if="!userStore.isLoggedIn && checkoutStore.isGuestMode" />
          
          <!-- Authenticated User Address -->
          <AddressSelector v-if="userStore.isLoggedIn" />

          <!-- Redeem Loyalty Points Section -->
          <div v-if="userStore.isLoggedIn" class="mt-10 border-t border-gray-200 pt-10">
            <h2 class="text-lg font-medium text-gray-900">Redeem Your Loyalty Points</h2>
            <p class="mt-1 text-sm text-gray-500">You have <span class="font-bold text-primary">{{ userStore.profile?.loyalty?.points || 0 }}</span> points to spend.</p>

            <div v-if="loyaltyStore.isLoading" class="mt-4">Loading rewards...</div>
            <div v-else-if="availableRewards.length > 0" class="mt-4 space-y-4">
              <div v-for="reward in availableRewards" :key="reward.id" class="flex items-center justify-between p-4 border rounded-md bg-white">
                <div>
                  <h4 class="font-semibold">{{ reward.name }}</h4>
                  <p class="text-sm text-gray-500">{{ reward.points_cost }} points</p>
                </div>
                <button @click="addRewardToCart(reward.id)" class="btn-secondary text-sm">
                  Add to Cart
                </button>
              </div>
            </div>
            <div v-else class="mt-4 text-gray-500">No rewards currently available for you to redeem.</div>
          </div>
          
          <!-- Delivery Methods -->
          <DeliveryMethodSelector class="mt-10 border-t border-gray-200 pt-10" />
        </div>

        <!-- Order summary -->
        <div class="mt-10 lg:mt-0">
          <OrderSummary />
          <div class="mt-6">
              <button type="button" class="w-full btn-primary" @click="proceedToPayment">Proceed to Payment</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '../../js/stores/user';
import { useCheckoutStore } from '../../js/stores/checkout';
import { useLoyaltyStore } from '../../js/stores/loyalty';
import { useCartStore } from '../../js/stores/cart';

import GuestCheckoutForm from '../components/checkout/GuestCheckoutForm.vue';
import AddressSelector from '../components/checkout/AddressSelector.vue';
import DeliveryMethodSelector from '../components/checkout/DeliveryMethodSelector.vue';
import OrderSummary from '../components/checkout/OrderSummary.vue';
import LoginForm from '../components/checkout/LoginForm.vue';

const userStore = useUserStore();
const checkoutStore = useCheckoutStore();
const loyaltyStore = useLoyaltyStore();
const cartStore = useCartStore();

const showLogin = ref(false);

onMounted(() => {
  if (userStore.isLoggedIn) {
    loyaltyStore.fetchExclusiveRewards();
  }
});

const availableRewards = computed(() => {
  if (!userStore.isLoggedIn || !userStore.profile?.loyalty) {
    return [];
  }
  const userPoints = userStore.profile.loyalty.points;
  return loyaltyStore.rewards.filter(reward => 
    reward.linked_product_id && 
    userPoints >= reward.points_cost && 
    !cartStore.items.some(item => item.product_id === reward.linked_product_id && item.is_reward)
  );
});

async function addRewardToCart(rewardId) {
    // This action should handle both the point deduction and adding the item to cart
    await cartStore.addRewardItem(rewardId);
    // Refresh user profile to get updated points total
    await userStore.checkAuthStatus(); 
    // Re-fetch rewards to update the list of what's available
    loyaltyStore.fetchExclusiveRewards();
}

function onLoginSuccess() {
    showLogin.value = false;
    loyaltyStore.fetchExclusiveRewards();
}

function proceedToPayment() {
    // This function will gather all the selected data from the checkoutStore,
    // userStore (for address), and cartStore, then call the appropriate API endpoint.
    const checkoutData = checkoutStore.getCheckoutData();
    console.log("Proceeding to payment with data:", checkoutData);
    alert('Proceeding to payment...');
}
</script>
