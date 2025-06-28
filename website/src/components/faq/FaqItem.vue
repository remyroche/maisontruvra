<template>
  <div class="border-b border-gray-200 py-4">
    <button @click="isOpen = !isOpen" class="w-full flex justify-between items-center text-left text-lg font-medium text-gray-900">
      <span>{{ faq.question }}</span>
      <svg :class="{'rotate-180': isOpen, 'text-gray-400': !isOpen, 'text-indigo-600': isOpen}" class="h-6 w-6 transform transition-transform duration-200" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    <div v-if="isOpen" class="mt-2 pr-12">
      <p class="text-base text-gray-600 leading-relaxed">
        {{ faq.answer }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  faq: {
    type: Object,
    required: true,
  },
});

const isOpen = ref(false);
</script>