<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Gérer les Demandes de Devis</h2>
    <div v-if="isLoading" class="text-center p-8">Chargement...</div>
    <div v-else>
      <BaseDataTable
        :items="quotes"
        :columns="columns"
        @view-item="openQuoteModal"
      >
        <template #cell-actions="{ item }">
           <button @click="openQuoteModal(item)" class="text-indigo-600 hover:text-indigo-900 font-medium">
              Voir et Créer la Facture
           </button>
        </template>
      </BaseDataTable>
    </div>
    
    <QuoteDetailModal 
        v-if="selectedQuote" 
        :quote="selectedQuote" 
        @close="selectedQuote = null"
        @invoice-created="handleInvoiceCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../../common/adminApiClient';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import QuoteDetailModal from '../components/QuoteDetailModal.vue';
import { useNotificationStore } from '../../stores/notification';

const quotes = ref([]);
const isLoading = ref(true);
const selectedQuote = ref(null);
const notificationStore = useNotificationStore();

const columns = [
  { key: 'id', label: 'ID Demande' },
  { key: 'company_name', label: 'Entreprise' },
  { key: 'created_at', label: 'Date', format: (date) => new Date(date).toLocaleDateString('fr-FR') },
  { key: 'user_request', label: 'Aperçu de la demande', truncate: 50 },
  { key: 'actions', label: 'Actions' },
];

async function fetchQuotes() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/admin/quotes');
    quotes.value = response.data;
  } catch (error) {
    notificationStore.showNotification('Erreur lors du chargement des devis.', 'error');
  } finally {
    isLoading.value = false;
  }
}

function openQuoteModal(quote) {
  selectedQuote.value = quote;
}

function handleInvoiceCreated() {
    selectedQuote.value = null;
    notificationStore.showNotification('Facture créée avec succès et en attente de signature.', 'success');
    fetchQuotes(); // Refresh the list to remove the converted quote
}

onMounted(fetchQuotes);
</script>
