<template>
  <div class="space-y-8">
    <!-- Main Header -->
    <div class="p-6 bg-white shadow rounded-lg">
      <h2 class="text-xl font-bold text-gray-900">{{ i18n.title }}</h2>
      <p class="mt-2 text-gray-600">{{ i18n.subtitle }}</p>
    </div>

    <!-- Referral Link Section -->
    <div class="p-6 bg-white shadow rounded-lg">
      <h3 class="text-lg font-semibold text-gray-800">{{ i18n.yourLinkTitle }}</h3>
      <div v-if="userStore.profile" class="mt-4 flex items-center space-x-4">
        <input type="text" :value="referralLink" readonly class="flex-grow p-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600">
        <button @click="copy(referralLink)" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 w-28">
          {{ copied ? i18n.copiedButton : i18n.copyButton }}
        </button>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="p-6 bg-white shadow rounded-lg">
      <h3 class="text-lg font-semibold text-gray-800">{{ i18n.howItWorksTitle }}</h3>
      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div v-for="(step, index) in i18n.steps" :key="step.title" class="text-center">
          <div class="flex items-center justify-center h-12 w-12 rounded-full bg-indigo-500 text-white font-bold text-lg mx-auto">
            {{ index + 1 }}
          </div>
          <h4 class="mt-4 font-semibold text-gray-900">{{ step.title }}</h4>
          <p class="mt-1 text-sm text-gray-600">{{ step.description }}</p>
        </div>
      </div>
    </div>

    <!-- Referral History Section -->
    <div class="p-6 bg-white shadow rounded-lg">
      <h3 class="text-lg font-semibold text-gray-800">{{ i18n.historyTitle }}</h3>
      <div class="mt-4">
        <p class="text-gray-500 italic">{{ i18n.historyComingSoon }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useClipboard } from '@vueuse/core';
import i18nData from '@/locales/pages/account-referrals.json';

const userStore = useUserStore();
const currentLang = ref('fr');
const i18n = computed(() => i18nData[currentLang.value]);

const referralLink = computed(() => {
  if (userStore.profile?.referral_code) {
    // Construct the full URL. This should ideally use a base URL from config.
    return `${window.location.origin}/register?ref=${userStore.profile.referral_code}`;
  }
  return '';
});

const { copy, copied } = useClipboard({ source: referralLink });

onMounted(() => {
  if (!userStore.profile) {
    userStore.fetchUserProfile();
  }
});
</script>