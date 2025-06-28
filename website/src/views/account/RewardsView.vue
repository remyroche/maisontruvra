<template>
  <div class="p-6 bg-white shadow rounded-lg">
    <h2 class="text-xl font-bold text-gray-900">{{ i18n.title }}</h2>
    <p class="mt-2 text-gray-600">{{ i18n.subtitle }}</p>

    <div class="mt-8">
        <h3 class="text-lg font-semibold text-gray-800">{{ i18n.availableRewardsTitle }}</h3>
        
        <div v-if="loyaltyStore.isLoading" class="text-center py-12">
            <p>{{ i18n.loading }}</p>
        </div>
        
        <div v-else-if="loyaltyStore.rewards.length > 0" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-8">
            <RewardCard
                v-for="reward in loyaltyStore.rewards"
                :key="reward.id"
                :reward="reward"
            />
        </div>
        <div v-else class="mt-6 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg p-8">
            <p>{{ i18n.noRewards }}</p>
        </div>
    </div>

    <div class="mt-12 border-t pt-8">
      <h3 class="text-lg font-semibold text-gray-800">{{ i18n.historyTitle }}</h3>
      <div class="mt-4">
        <p class="text-gray-500 italic">{{ i18n.historyComingSoon }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useLoyaltyStore } from '@/stores/loyalty';
import RewardCard from '@/components/rewards/RewardCard.vue';
import i18nData from '@/locales/pages/account-rewards.json';

const loyaltyStore = useLoyaltyStore();
const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

onMounted(() => {
    loyaltyStore.fetchExclusiveRewards();
});
</script>