<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Quotes</h1>

    <div v-if="quotesStore.isLoading" class="text-center p-4">Loading quotes...</div>
    <div v-if="quotesStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ quotesStore.error }}</div>

    <BaseDataTable
      v-if="!quotesStore.isLoading"
      :headers="headers"
      :items="quotesStore.quotes"
    >
        <template #item-status="{ item }">
            <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="statusClass(item.status)">
            {{ item.status }}
            </span>
        </template>
        <template #item-actions="{ item }">
            <button @click="openDetailsModal(item.id)" class="text-indigo-600 hover:text-indigo-900 mr-4">View</button>
            <button v-if="item.status === 'pending'" @click="convertQuote(item.id)" class="text-green-600 hover:text-green-900 mr-4">Convert to Order</button>
            <button @click="deleteQuote(item.id)" class="text-red-600 hover:text-red-900">Delete</button>
        </template>
    </BaseDataTable>
    
    <Modal :is-open="isModalOpen" @close="closeModal">
        <h2 class="text-xl font-bold mb-4">Quote Details</h2>
        <div v-if="quotesStore.quote" class="space-y-4">
            <p><strong>Quote ID:</strong> #{{ quotesStore.quote.id }}</p>
            <p><strong>Customer:</strong> {{ quotesStore.quote.customer_name }}</p>
            <ul>
                <li v-for="item in quotesStore.quote.items" :key="item.id" class="border-t py-2">
                    {{ item.product_name }} - {{ item.quantity }} x ${{ item.price }}
                </li>
            </ul>
            <p class="font-bold text-right">Total: ${{ quotesStore.quote.total_amount }}</p>
        </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminQuotesStore } from '@/js/stores/adminQuotes';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';

const quotesStore = useAdminQuotesStore();
const isModalOpen = ref(false);

const headers = [
  { text: 'Quote ID', value: 'id' },
  { text: 'Customer', value: 'customer_name' },
  { text: 'Date', value: 'created_at' },
  { text: 'Total', value: 'total_amount' },
  { text: 'Status', value: 'status' },
  { text: 'Actions', value: 'actions' },
];

onMounted(() => quotesStore.fetchQuotes());

const openDetailsModal = (id) => {
    quotesStore.fetchQuoteDetails(id);
    isModalOpen.value = true;
};
const closeModal = () => {
    isModalOpen.value = false;
    quotesStore.quote = null;
};
const convertQuote = (id) => {
    if(confirm('Convert this quote to a draft order?')) {
        quotesStore.convertQuoteToOrder(id);
    }
};
const deleteQuote = (id) => {
    if(confirm('Are you sure you want to delete this quote?')) {
        quotesStore.deleteQuote(id);
    }
};
const statusClass = (status) => ({
  'pending': 'bg-yellow-100 text-yellow-800',
  'converted': 'bg-green-100 text-green-800',
  'expired': 'bg-gray-100 text-gray-800',
}[status]);
</script>
