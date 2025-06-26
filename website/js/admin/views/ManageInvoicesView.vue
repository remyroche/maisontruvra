<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Gérer les Factures</h2>
    
    <!-- Filter Controls -->
    <div class="mb-4">
        <label for="status-filter" class="mr-2 font-semibold">Filtrer par statut:</label>
        <select id="status-filter" v-model="statusFilter" @change="fetchInvoices(1)" class="p-2 border rounded-md">
            <option value="">Tous</option>
            <option value="draft">Brouillon</option>
            <option value="pending_signature">En attente de signature</option>
            <option value="signed">Signée</option>
            <option value="paid">Payée</option>
            <option value="void">Annulée</option>
        </select>
    </div>

    <div v-if="isLoading" class="text-center p-8">Chargement...</div>
    <div v-else>
      <BaseDataTable
        :items="invoices"
        :columns="columns"
        @view-item="viewInvoiceDetail"
      />
      <Pagination
        v-if="pagination.total > 0"
        :current-page="pagination.currentPage"
        :per-page="pagination.perPage"
        :total="pagination.total"
        :has-prev="pagination.hasPrev"
        :has-next="pagination.hasNext"
        @previous="fetchInvoices(pagination.currentPage - 1)"
        @next="fetchInvoices(pagination.currentPage + 1)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../common/adminApiClient';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import Pagination from '../components/ui/Pagination.vue'; // Assuming pagination component exists
import { useNotificationStore } from '../../stores/notification';

const invoices = ref([]);
const isLoading = ref(true);
const statusFilter = ref('');
const router = useRouter();
const notificationStore = useNotificationStore();

const pagination = reactive({
    currentPage: 1,
    perPage: 10,
    total: 0,
    hasPrev: false,
    hasNext: false,
});

const columns = [
  { key: 'id', label: 'Facture N°' },
  { key: 'company_name', label: 'Entreprise' },
  { key: 'total_amount', label: 'Montant', format: val => `${val.toFixed(2)} €` },
  { key: 'status', label: 'Statut' },
  { key: 'created_at', label: 'Date Création', format: (date) => new Date(date).toLocaleDateString('fr-FR') },
  { key: 'due_date', label: 'Échéance', format: (date) => date ? new Date(date).toLocaleDateString('fr-FR') : 'N/A' },
];

async function fetchInvoices(page = 1) {
  isLoading.value = true;
  try {
    const params = new URLSearchParams({
        page: page,
        per_page: pagination.perPage
    });
    if (statusFilter.value) {
        params.append('status', statusFilter.value);
    }
    const response = await apiClient.get('/admin/invoices', { params });
    invoices.value = response.data.invoices;
    pagination.total = response.data.total;
    pagination.currentPage = response.data.current_page;
    pagination.hasPrev = response.data.has_prev;
    pagination.hasNext = response.data.has_next;

  } catch (error) {
    notificationStore.showNotification('Erreur lors du chargement des factures.', 'error');
  } finally {
    isLoading.value = false;
  }
}

function viewInvoiceDetail(invoice) {
    // Assuming you will create a detail view for admin
    // router.push({ name: 'AdminInvoiceDetail', params: { id: invoice.id } });
    console.log("Viewing invoice:", invoice.id)
}

onMounted(() => fetchInvoices());
</script>
