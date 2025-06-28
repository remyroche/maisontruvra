<template>
  <div class="bg-white py-24 sm:py-32">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="mx-auto max-w-2xl lg:mx-0">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ content.title }}</h2>
        <p class="mt-6 text-lg leading-8 text-gray-600">{{ content.subtitle }}</p>
      </div>
      <div class="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 text-base leading-7 sm:grid-cols-2 lg:mx-0 lg:max-w-none lg:grid-cols-4">
        <div v-for="section in content.sections" :key="section.title">
          <h3 class="font-semibold text-gray-900">{{ section.title }}</h3>
          <p class="mt-2 text-gray-600">{{ section.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import i18nData from '@/locales/pages/charte-qualite.json';

// This would typically come from a global i18n store or plugin.
// For this component, we'll default to 'fr' to match the site's primary language.
const currentLang = ref('fr'); 

const content = computed(() => i18nData[currentLang.value]);
</script>