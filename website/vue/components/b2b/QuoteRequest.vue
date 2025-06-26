<template>
  <div class="p-6 bg-cream rounded-lg shadow-md">
    <h3 class="text-2xl font-serif text-truffle-burgundy mb-4">Demande de Devis Personnalisé</h3>
    <p class="text-dark-brown mb-6">Pour des besoins spécifiques, veuillez décrire votre demande ci-dessous. Notre équipe vous enverra une facture personnalisée.</p>
    <form @submit.prevent="submitRequest">
      <div class="mb-4">
        <label for="request-details" class="block text-sm font-medium text-dark-brown mb-2">Détails de votre demande</label>
        <textarea 
          id="request-details" 
          v-model="requestDetails"
          rows="6"
          class="w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold"
          placeholder="Ex: Quantités, produits spécifiques, demandes de packaging..."
          required
        ></textarea>
      </div>
      <button type="submit" :disabled="isLoading" class="btn-primary py-2 px-6 rounded-md disabled:opacity-50">
        <span v-if="!isLoading">Envoyer la Demande</span>
        <span v-else>Envoi en cours...</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '../../js/api-client';
import { useNotificationStore } from '../../js/stores/notification';

const requestDetails = ref('');
const isLoading = ref(false);
const notificationStore = useNotificationStore();

async function submitRequest() {
  isLoading.value = true;
  try {
    await apiClient.post('/api/b2b/quotes', { request_details: requestDetails.value });
    notificationStore.showNotification('Votre demande de devis a été envoyée avec succès.', 'success');
    requestDetails.value = '';
  } catch (error) {
    notificationStore.showNotification(error.response?.data?.error || 'Échec de l\'envoi de la demande.', 'error');
  } finally {
    isLoading.value = false;
  }
}
