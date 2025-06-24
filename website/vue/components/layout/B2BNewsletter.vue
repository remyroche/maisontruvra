<template>
  <div>
    <h3 class="text-base font-semibold text-gray-900">Newsletter Pro</h3>
    <p class="mt-2 text-sm text-gray-600">Restez informés des nouveautés et offres pour les professionnels.</p>
    <form @submit.prevent="subscribe" class="mt-4 sm:flex sm:max-w-md">
      <label for="b2b-email-address" class="sr-only">Adresse e-mail</label>
      <input
        type="email"
        name="b2b-email-address"
        id="b2b-email-address"
        v-model="email"
        autocomplete="email"
        required
        class="w-full min-w-0 appearance-none rounded-md border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 placeholder-gray-500 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        placeholder="Votre adresse e-mail pro"
        :disabled="loading"
      />
      <div class="mt-3 rounded-md sm:mt-0 sm:ml-3 sm:flex-shrink-0">
        <button
          type="submit"
          class="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          :disabled="loading"
        >
          <span v-if="!loading">S'inscrire</span>
          <span v-else class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            ...
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '../../../js/api-client';
import { useNotificationStore } from '../../../js/stores/notification';

const email = ref('');
const loading = ref(false);
const notificationStore = useNotificationStore();

/**
 * Handles the B2B newsletter subscription form submission.
 */
const subscribe = async () => {
  if (!email.value || !/^\S+@\S+\.\S+$/.test(email.value)) {
    notificationStore.showNotification('Veuillez entrer une adresse e-mail valide.', 'error');
    return;
  }

  loading.value = true;
  try {
    const response = await apiClient.subscribeB2B(email.value);
    notificationStore.showNotification(response.message || 'Merci pour votre inscription à notre newsletter professionnelle !', 'success');
    email.value = ''; // Clear input on success
  } catch (error) {
    console.error('B2B Newsletter subscription error:', error);
    const errorMessage = error.data?.error || 'Une erreur est survenue lors de l\'inscription.';
    notificationStore.showNotification(errorMessage, 'error');
  } finally {
    loading.value = false;
  }
};
</script>
