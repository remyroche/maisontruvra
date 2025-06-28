<template>
  <div class="bg-white">
    <div class="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 lg:py-40">
      <div class="mx-auto max-w-4xl divide-y divide-gray-900/10">
        <h2 class="text-2xl font-bold leading-10 tracking-tight text-gray-900">Frequently Asked Questions</h2>
        
        <div class="mt-6 border-b border-gray-200">
            <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                <router-link 
                    :to="{ name: 'FaqB2C' }" 
                    :class="[$route.name === 'FaqB2C' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']"
                >
                    General
                </router-link>
                <router-link 
                    :to="{ name: 'FaqB2B' }" 
                    :class="[$route.name === 'FaqB2B' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']"
                >
                    Professional
                </router-link>
            </nav>
        </div>

        <div class="mt-10">
            <div v-if="faqStore.isLoading" class="text-center py-12">Loading...</div>
            <div v-else-if="faqStore.error" class="text-center py-12 text-red-600">{{ faqStore.error }}</div>
            <router-view v-else />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useFaqStore } from '@/stores/faq';

const faqStore = useFaqStore();

onMounted(() => {
  faqStore.fetchFaqs();
});
</script>
