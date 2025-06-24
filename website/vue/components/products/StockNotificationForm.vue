<template>
  <div class="mt-6 p-4 bg-gray-100 rounded-lg">
    <h3 class="text-base font-medium text-gray-900">Produit indisponible</h3>
    <p class="text-sm text-gray-600 mt-1">Laissez-nous votre e-mail pour être prévenu dès son retour en stock.</p>
    
    <Form @submit="requestNotification" class="mt-4">
      <div v-if="!authStore.isAuthenticated" class="mb-4">
        <label for="email-stock-notification" class="sr-only">Adresse e-mail</label>
        <Field 
          name="email" 
          type="email" 
          id="email-stock-notification" 
          v-model="guestEmail" 
          rules="required|email" 
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="votre@email.com"
        />
        <ErrorMessage name="email" class="text-sm text-red-600 mt-1" />
      </div>

       <button type="submit" :disabled="loading || submitted" class="w-full flex items-center justify-center rounded-md border border-transparent bg-indigo-600 py-3 px-8 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
        <span v-if="loading">Envoi en cours...</span>
        <span v-else-if="submitted">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>
            Notification enregistrée !
        </span>
        <span v-else>Prévenez-moi</span>
      </button>
    </Form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../../js/stores/auth';
import { useNotificationStore } from '../../js/stores/notification';
import apiClient from '../../js/api-client';
import { Form, Field, ErrorMessage } from 'vee-validate';

const props = defineProps({
  productId: { type: Number, required: true }
});

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const guestEmail = ref('');
const loading = ref(false);
const submitted = ref(false);

async function requestNotification() {
  loading.value = true;
  try {
    const payload = authStore.isAuthenticated ? {} : { email: guestEmail.value };
    // This new API client method needs to be created
    await apiClient.requestStockNotification(props.productId, payload);
    submitted.value = true;
    notificationStore.showNotification('Vous serez prévenu dès que ce produit sera de retour !', 'success');
  } catch (error) {
    // Display a more specific message if the user is already on the list
    const errorMessage = error.data?.error || 'Une erreur est survenue.';
    notificationStore.showNotification(errorMessage, 'error');
  } finally {
    loading.value = false;
  }
}
</script>
