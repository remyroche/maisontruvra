<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-10" @close="open = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed z-10 inset-0 overflow-y-auto">
        <div class="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel v-if="reward" class="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-lg sm:w-full sm:p-6">
              <div>
                <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-indigo-100">
                   <svg class="h-10 w-10 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1014.625 7.5H9.375A2.625 2.625 0 1012 4.875z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.875v.001M12 12.75v.001M12 21.75v.001M12 12.75a2.625 2.625 0 100-5.25 2.625 2.625 0 000 5.25z" />
                   </svg>
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-lg leading-6 font-medium text-gray-900"> A Gift for Your Loyalty </DialogTitle>
                  <div class="mt-2">
                     <p class="text-sm text-gray-500">As a token of our appreciation, please enjoy this complimentary</p>
                     <p class="text-xl font-semibold text-gray-800 mt-1">{{ reward.name }}</p>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6">
                <button type="button" class="inline-flex justify-center w-full rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:text-sm" @click="claimReward">
                  Add to My Order
                </button>
                 <button type="button" class="mt-3 inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:text-sm" @click="$emit('close')">
                  Maybe next time
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'

const props = defineProps({
  open: Boolean,
  reward: Object,
});
const emit = defineEmits(['close', 'claim']);

function claimReward() {
  emit('claim', props.reward.id);
  emit('close');
}
</script>
```

### **2. Updated Checkout View with Modal Integration**

The checkout page now uses the new modal to create a more engaging experience.


```vue
<template>
  <div class="bg-gray-50">
    <div class="mx-auto max-w-2xl px-4 pt-16 pb-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h2 class="sr-only">Checkout</h2>

      <div class="lg:grid lg:grid-cols-2 lg:gap-x-12 xl:gap-x-16">
        <div>
          <!-- ... Guest/Login and Address sections ... -->
          
          <!-- Redeem Loyalty Points Section - Updated -->
          <div v-if="userStore.isLoggedIn" class="mt-10 border-t border-gray-200 pt-10">
            <h2 class="text-lg font-medium text-gray-900">A Gift for You?</h2>
            <p class="mt-1 text-sm text-gray-500">You have <span class="font-bold text-primary">{{ userStore.profile?.loyalty?.points || 0 }}</span> points to spend.</p>

            <div v-if="loyaltyStore.isLoading" class="mt-4">Loading rewards...</div>
            <div v-else-if="availableRewards.length > 0" class="mt-4 space-y-4">
              <div v-for="reward in availableRewards" :key="reward.id" class="flex items-center justify-between p-4 border rounded-md bg-white">
                <div>
                  <h4 class="font-semibold">{{ reward.name }}</h4>
                  <p class="text-sm text-gray-500">{{ reward.points_cost }} points</p>
                </div>
                <!-- This button now opens the modal -->
                <button @click="openRewardModal(reward)" class="btn-secondary text-sm">
                  Claim Your Gift
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
          <!-- ... proceed to payment button ... -->
        </div>
      </div>
    </div>
    
    <!-- The Reward Modal -->
    <RewardModal :open="isRewardModalOpen" :reward="selectedReward" @close="isRewardModalOpen = false" @claim="addRewardToCart" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '../../js/stores/user';
import { useCheckoutStore } from '../../js/stores/checkout';
import { useLoyaltyStore } from '../../js/stores/loyalty';
import { useCartStore } from '../../js/stores/cart';

// ... other component imports
import OrderSummary from '../components/checkout/OrderSummary.vue';
import DeliveryMethodSelector from '../components/checkout/DeliveryMethodSelector.vue';
import RewardModal from '../components/rewards/RewardModal.vue'; // Import the new modal

const userStore = useUserStore();
const checkoutStore = useCheckoutStore();
const loyaltyStore = useLoyaltyStore();
const cartStore = useCartStore();

const isRewardModalOpen = ref(false);
const selectedReward = ref(null);

onMounted(() => {
  if (userStore.isLoggedIn) {
    loyaltyStore.fetchExclusiveRewards();
  }
});

const availableRewards = computed(() => {
  if (!userStore.isLoggedIn || !userStore.profile?.loyalty) return [];
  const userPoints = userStore.profile.loyalty.points;
  return loyaltyStore.rewards.filter(reward => 
    reward.linked_product_id && 
    userPoints >= reward.points_cost && 
    !cartStore.items.some(item => item.product_id === reward.linked_product_id && item.is_reward)
  );
});

function openRewardModal(reward) {
  selectedReward.value = reward;
  isRewardModalOpen.value = true;
}

async function addRewardToCart(rewardId) {
    await cartStore.addRewardItem(rewardId);
    await userStore.checkAuthStatus(); // Refresh points
    loyaltyStore.fetchExclusiveRewards(); // Refresh available rewards
}
</script>
