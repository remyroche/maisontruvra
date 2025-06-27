<template>
  <div class="bg-gray-50">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          The Truffle Treasury
        </h2>
        <p class="mt-4 text-lg text-gray-500">
          Redeem your loyalty points for exclusive products and unique experiences.
        </p>
      </div>

      <div v-if="loyaltyStore.isLoading" class="text-center mt-8">
        <p>Loading rewards...</p>
      </div>
      
      <div v-else-if="loyaltyStore.rewards.length === 0" class="text-center mt-8 bg-white p-8 rounded-lg shadow">
          <h3 class="text-xl font-medium text-gray-800">No Rewards Available Yet</h3>
          <p class="text-gray-500 mt-2">Check back soon, or continue shopping to unlock rewards for higher tiers!</p>
      </div>

      <div v-else class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <RewardCard v-for="reward in loyaltyStore.rewards" :key="reward.id" :reward="reward" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useLoyaltyStore } from '../../js/stores/loyalty';
import RewardCard from '../components/rewards/RewardCard.vue';

const loyaltyStore = useLoyaltyStore();

onMounted(() => {
  loyaltyStore.fetchExclusiveRewards();
});
</script>
