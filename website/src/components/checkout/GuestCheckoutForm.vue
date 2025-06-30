<template>
  <div>
    <h3 class="text-lg font-medium text-gray-900">Coordonnées</h3>
    <form @submit.prevent="handleContinue" class="mt-6">
      <UserDetailsForm v-model="guestDetails" />
      <div class="mt-6">
        <button type="submit"
                class="w-full rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
          Continuer
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import UserDetailsForm from '@/components/forms/UserDetailsForm.vue';

// This component now uses the generic UserDetailsForm.

const emit = defineEmits(['continue']);

const guestDetails = ref({
  firstName: '',
  lastName: '',
  email: ''
});

const handleContinue = () => {
  // Here you would add validation logic
  emit('continue', { ...guestDetails.value });
};
</script>
