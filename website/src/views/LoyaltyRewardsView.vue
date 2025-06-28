<template>
  <div class="container mx-auto py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Our Loyalty Rewards</h1>
    <p class="text-lg text-gray-600 mb-8">Redeem your points for exclusive products and experiences.</p>

    <div v-if="isLoading" class="text-center py-12">
      <p>Loading rewards...</p>
    </div>

    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Oops!</strong>
      <span class="block sm:inline"> Something went wrong while fetching rewards. Please try again later.</span>
    </div>

    <div v-if="rewards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <RewardCard
        v-for="reward in rewards"
        :key="reward.id"
        :reward="reward"
      />
    </div>
  </div>
</template>

<script setup>
import { useApiData } from '@/src/composables/useApiData';
import { apiClient } from '@/src/services/api';
import RewardCard from '@/vue/components/rewards/RewardCard.vue';

const { data: rewards, isLoading, error } = useApiData(() => apiClient.get('/loyalty/rewards'));
</script>