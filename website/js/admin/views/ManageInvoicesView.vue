<!--
 * FILENAME: website/js/admin/views/ManageInvoicesView.vue
 * DESCRIPTION: New view for displaying and managing invoices.
-->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <header>
                <h1 class="text-3xl font-bold text-gray-800">Manage Invoices</h1>
                <p class="text-gray-500 mt-1">View and download generated invoices for all orders.</p>
            </header>

            <div v-if="invoiceStore.isLoading" class="text-center py-10">Loading invoices...</div>
            <div v-else-if="invoiceStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ invoiceStore.error }}</div>
            
            <BaseDataTable v-else :columns="columns" :data="invoiceStore.invoices">
                <template #cell(order_id)="{ value }">
                    <span class="font-mono text-sm">#{{ value }}</span>
                </template>
                 <template #cell(total_amount)="{ value }">
                    €{{ value.toFixed(2) }}
                </template>
                 <template #cell(invoice_date)="{ value }">
                    {{ new Date(value).toLocaleDateString() }}
                </template>
                <template #cell(actions)="{ item }">
                    <a :href="`/api/admin/invoices/${item.id}/download`" 
                       target="_blank" 
                       class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded text-xs">
                       Download PDF
                    </a>
                </template>
            </BaseDataTable>
        </div>
    </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminInvoiceStore } from '../../stores/adminInvoices';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const invoiceStore = useAdminInvoiceStore();

const columns = [
    { key: 'id', label: 'Invoice ID' },
    { key: 'order_id', label: 'Order ID' },
    { key: 'customer_name', label: 'Customer' },
    { key: 'invoice_date', label: 'Date' },
    { key: 'total_amount', label: 'Amount', cellClass: 'text-right' },
    { key: 'actions', label: 'Actions', cellClass: 'text-right' },
];

onMounted(() => {
    invoiceStore.fetchInvoices();
});
</script>
