
<template>
  <div class="container mx-auto px-6 max-w-3xl">
    <h1 class="text-5xl font-serif font-thin text-center mb-8">{{ t('privacyPolicy') }}</h1>
    <div id="privacy-policy-content" class="text-lg text-dark-gray leading-relaxed space-y-6">
      <p>{{ t('lastUpdated') }}</p>

      <h2 class="text-3xl font-serif font-light text-dark-brown pt-6">{{ t('section1Title') }}</h2>
      <p>
        {{ t('section1Text') }}
      </p>

      <h2 class="text-3xl font-serif font-light text-dark-brown pt-6">{{ t('section2Title') }}</h2>
      <p>
        {{ t('section2Text') }}
      </p>

      <h2 class="text-3xl font-serif font-light text-dark-brown pt-6">{{ t('section3Title') }}</h2>
      <p>
        {{ t('section3Text') }}
      </p>
      
      </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { initI18n, t } from '../../js/i18n'; // Adjust the import path as necessary

onMounted(() => {
  // Ensure i18n is initialized and content is updated when this component mounts
  initI18n();
});
</script>

<style scoped>
/* Add any component-specific styles here if necessary */
</style>
