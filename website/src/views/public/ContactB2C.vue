<template>
  <div class="bg-white py-16 sm:py-24">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ $t('contact.title') }}</h2>
        <p class="mt-2 text-lg leading-8 text-gray-600">
          {{ $t('contact.subtitle') }}
        </p>
      </div>

      <!-- Integrating the new validated contact form -->
      <div class="mx-auto mt-16 max-w-xl sm:mt-20">
        <ContactForm />
      </div>

    </div>
  </div>
</template>

<script setup>
import ContactForm from '@/components/forms/ContactForm.vue';
</script>
