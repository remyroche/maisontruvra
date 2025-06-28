<template>
  <div class="isolate bg-white px-6 py-24 sm:py-32 lg:px-8">
    <div class="mx-auto max-w-2xl text-center">
      <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ content.title }}</h2>
      <p class="mt-2 text-lg leading-8 text-gray-600">{{ content.subtitle }}</p>
    </div>
    <form @submit.prevent="submitForm" class="mx-auto mt-16 max-w-xl sm:mt-20">
      <div class="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
        <!-- Form fields would go here -->
        <div>
          <label for="company-name" class="block text-sm font-semibold leading-6 text-gray-900">Company Name</label>
          <div class="mt-2.5">
            <input type="text" name="company-name" id="company-name" autocomplete="organization" class="block w-full rounded-md border-0 px-3.5 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
          </div>
        </div>
        <!-- ... other B2B specific fields -->
      </div>
      <div class="mt-10">
        <button type="submit" class="block w-full rounded-md bg-indigo-600 px-3.5 py-2.5 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Send Message</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import i18nData from '@/locales/pages/contact-b2b.json';

const currentLang = ref('fr'); 
const content = computed(() => i18nData[currentLang.value]);

function submitForm() {
  // Handle B2B form submission
  console.log('Submitting B2B contact form...');
}
</script>