<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Invoices</h1>

     <div v-if="invoicesStore.isLoading" class="text-center p-4">Loading invoices...</div>
    <div v-if="invoicesStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ invoicesStore.error }}</div>

    <BaseDataTable
      v-if="!invoicesStore.isLoading"
      :headers="headers"
      :items="invoicesStore.invoices"
    >
      <template #item-status="{ item }">
        <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="statusClass(item.status)">
          {{ item.status }}
        </span>
      </template>
      <template #item-actions="{ item }">
        <button @click="downloadInvoice(item.id)" class="text-indigo-600 hover:text-indigo-900">Download PDF</button>
      </template>
    </BaseDataTable>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminInvoicesStore } from '@/js/stores/adminInvoices';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const invoicesStore = useAdminInvoicesStore();

const headers = [
    { text: 'Invoice #', value: 'id' },
    { text: 'Order ID', value: 'order_id' },
    { text: 'Customer', value: 'customer_name' },
    { text: 'Date', value: 'created_at' },
    { text: 'Amount', value: 'total_amount' },
    { text: 'Status', value: 'status' },
    { text: 'Actions', value: 'actions' },
];

onMounted(() => invoicesStore.fetchInvoices());

const downloadInvoice = (id) => {
    invoicesStore.downloadInvoice(id);
};

const statusClass = (status) => ({
  'paid': 'bg-green-100 text-green-800',
  'pending': 'bg-yellow-100 text-yellow-800',
  'overdue': 'bg-red-100 text-red-800',
}[status]);

</script>
