<template>
  <div class="bg-white px-6 py-32 lg:px-8">
    <div class="mx-auto max-w-3xl text-base leading-7 text-gray-700">
      <p class="text-base font-semibold leading-7 text-indigo-600">{{ content.lastUpdated }}</p>
      <h1 class="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ content.title }}</h1>
      <p class="mt-6 text-xl leading-8">{{ content.introduction }}</p>
      <div class="mt-10 max-w-2xl">
        <div v-for="section in content.sections" :key="section.title" class="mt-8">
          <h2 class="text-2xl font-bold tracking-tight text-gray-900">{{ section.title }}</h2>
          <p class="mt-6">{{ section.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import i18nData from '@/locales/pages/politique-confidentialite.json';

// This would typically come from a global i18n store or plugin.
// For this component, we'll default to 'fr' to match the site's primary language.
const currentLang = ref('fr'); 

const content = computed(() => i18nData[currentLang.value]);
</script>