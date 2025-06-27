<template>
  <div class="flex flex-col rounded-lg shadow-lg overflow-hidden">
    <div class="flex-shrink-0">
      <!-- You can add specific images for rewards later -->
      <img class="h-48 w-full object-cover" src="https://placehold.co/600x400/2c2c2c/ffffff?text=Reward" :alt="reward.name">
    </div>
    <div class="flex-1 bg-white p-6 flex flex-col justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-indigo-600">
          {{ reward.reward_type.charAt(0).toUpperCase() + reward.reward_type.slice(1) }}
        </p>
        <a href="#" class="block mt-2">
          <p class="text-xl font-semibold text-gray-900">{{ reward.name }}</p>
          <p class="mt-3 text-base text-gray-500">{{ reward.description }}</p>
        </a>
      </div>
      <div class="mt-6 flex items-center justify-between">
        <div class="flex items-center">
          <p class="text-lg font-bold text-gray-900">{{ reward.points_cost }} Points</p>
        </div>
        <button @click="handleRedeem" class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-indigo-700">
          Redeem
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLoyaltyStore } from '../../../js/stores/loyalty';
import { useUserStore } from '../../../js/stores/user';

const props = defineProps({
  reward: {
    type: Object,
    required: true,
  },
});

const loyaltyStore = useLoyaltyStore();
const userStore = useUserStore(); // To check if user can afford it

const handleRedeem = async () => {
  // Optional: Add a client-side check for points before calling the API
  if(userStore.profile?.loyalty?.points < props.reward.points_cost) {
      useNotificationStore().showNotification({ message: "You don't have enough points for this reward.", type: 'warning' });
      return;
  }
  
  const success = await loyaltyStore.redeemReward(props.reward.id);
  if (success) {
    // You could refresh user data to show updated points total
    // userStore.fetchUserProfile();
  }
};
</script>
