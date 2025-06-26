<template>
  <div class="p-6">
    <h3 class="text-2xl font-serif text-truffle-burgundy mb-4">Mes Factures</h3>
    <div v-if="isLoading" class="text-center">Chargement des factures...</div>
    <div v-else-if="invoices.length === 0" class="text-center text-gray-500">
      Vous n'avez aucune facture pour le moment.
    </div>
    <div v-else class="space-y-4">
      <div v-for="invoice in invoices" :key="invoice.id" class="bg-white p-4 rounded-lg shadow-sm flex justify-between items-center">
        <div>
          <p class="font-bold text-dark-brown">Facture #{{ invoice.id }}</p>
          <p class="text-sm text-gray-600">Montant: {{ formatCurrency(invoice.total_amount) }}</p>
          <p class="text-sm text-gray-600">Date: {{ formatDate(invoice.created_at) }}</p>
        </div>
        <div>
          <span :class="statusClass(invoice.status)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase">
            {{ invoice.status.replace('_', ' ') }}
          </span>
          <button @click="viewInvoice(invoice.id)" class="ml-4 btn-secondary text-sm py-1 px-3 rounded-md">
            Voir
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../js/api-client';

const invoices = ref([]);
const isLoading = ref(true);
const router = useRouter();

async function fetchInvoices() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/api/b2b/invoices');
    invoices.value = response.data;
  } catch (error) {
    console.error("Failed to fetch invoices:", error);
  } finally {
    isLoading.value = false;
  }
}

function viewInvoice(id) {
  router.push({ name: 'B2BInvoiceDetail', params: { id } });
}

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value);
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR');
}

function statusClass(status) {
  const classes = {
    'pending_signature': 'bg-yellow-200 text-yellow-800',
    'signed': 'bg-blue-200 text-blue-800',
    'paid': 'bg-green-200 text-green-800',
    'draft': 'bg-gray-200 text-gray-800',
    'void': 'bg-red-200 text-red-800',
  };
  return classes[status] || 'bg-gray-200';
}

onMounted(fetchInvoices);
</script>
