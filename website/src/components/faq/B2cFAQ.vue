<template>
  <div class="space-y-4">
    <FaqItem v-for="item in faqStore.faqs.b2c" :key="item.id" :faq="item" />
  </div>
</template>

<script setup>
import { useFaqStore } from '@/stores/faq';
import FaqItem from './FaqItem.vue';

const faqStore = useFaqStore();
</script>