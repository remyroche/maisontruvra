<template>
  <Modal @close="$emit('close')">
    <template #header>
      <h3 class="text-lg font-medium leading-6 text-gray-900">
        Devis de {{ quote.company_name }}
      </h3>
    </template>
    <template #body>
        <div class="mt-2">
            <p class="text-sm font-bold text-gray-600">Demande du client :</p>
            <p class="text-sm text-gray-800 bg-gray-100 p-3 rounded-md mt-1 whitespace-pre-wrap">{{ quote.user_request }}</p>
        </div>
        <hr class="my-4">
        <div>
            <h4 class="text-md font-semibold text-gray-800 mb-3">Créer la Facture</h4>
            <div v-for="(item, index) in invoiceItems" :key="index" class="grid grid-cols-12 gap-2 items-center mb-2">
                <input v-model="item.description" type="text" placeholder="Description" class="col-span-6 p-2 border rounded-md">
                <input v-model.number="item.quantity" type="number" placeholder="Qté" class="col-span-2 p-2 border rounded-md">
                <input v-model.number="item.unit_price" type="number" step="0.01" placeholder="Prix Unitaire" class="col-span-3 p-2 border rounded-md">
                <button @click="removeItem(index)" class="col-span-1 text-red-500 hover:text-red-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </div>
             <button @click="addItem" class="text-sm font-medium text-indigo-600 hover:text-indigo-800 mt-2">+ Ajouter une ligne</button>
             <div class="mt-4">
                <label for="due_date" class="block text-sm font-medium text-gray-700">Date d'échéance (optionnel)</label>
                <input type="date" v-model="dueDate" id="due_date" class="p-2 border rounded-md">
             </div>
        </div>
    </template>
    <template #footer>
        <div class="flex justify-end space-x-3">
             <button @click="$emit('close')" type="button" class="btn-secondary rounded-md py-2 px-4">Annuler</button>
             <button @click="createInvoice" type="button" class="btn-primary rounded-md py-2 px-4" :disabled="invoiceItems.length === 0">
                Créer et Envoyer pour Signature
            </button>
        </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, reactive } from 'vue';
import Modal from './Modal.vue';
import apiClient from '../../common/adminApiClient';

const props = defineProps({
  quote: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close', 'invoice-created']);

const invoiceItems = reactive([
  { description: '', quantity: 1, unit_price: 0 },
]);
const dueDate = ref('');

function addItem() {
  invoiceItems.push({ description: '', quantity: 1, unit_price: 0 });
}

function removeItem(index) {
  invoiceItems.splice(index, 1);
}

async function createInvoice() {
  try {
    const payload = {
        items: invoiceItems,
        due_date: dueDate.value || null,
    };
    await apiClient.post(`/admin/quotes/${props.quote.id}/convert-to-invoice`, payload);
    emit('invoice-created');
  } catch (error) {
    console.error("Failed to create invoice:", error);
    // TODO: show notification
  }
}
</script>
```

```html
<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Gérer les Factures</h2>
    
    <!-- Filter Controls -->
    <div class="mb-4">
        <label for="status-filter" class="mr-2 font-semibold">Filtrer par statut:</label>
        <select id="status-filter" v-model="statusFilter" @change="fetchInvoices" class="p-2 border rounded-md">
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../common/adminApiClient';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import { useNotificationStore } from '../../stores/notification';

const invoices = ref([]);
const isLoading = ref(true);
const statusFilter = ref('');
const router = useRouter();
const notificationStore = useNotificationStore();

const columns = [
  { key: 'id', label: 'Facture N°' },
  { key: 'company_name', label: 'Entreprise' },
  { key: 'total_amount', label: 'Montant', format: val => `${val.toFixed(2)} €` },
  { key: 'status', label: 'Statut' },
  { key: 'created_at', label: 'Date Création', format: (date) => new Date(date).toLocaleDateString('fr-FR') },
  { key: 'due_date', label: 'Échéance', format: (date) => date ? new Date(date).toLocaleDateString('fr-FR') : 'N/A' },
];

async function fetchInvoices() {
  isLoading.value = true;
  try {
    const params = new URLSearchParams();
    if (statusFilter.value) {
        params.append('status', statusFilter.value);
    }
    const response = await apiClient.get('/admin/invoices', { params });
    invoices.value = response.data;
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

onMounted(fetchInvoices);
</script>
