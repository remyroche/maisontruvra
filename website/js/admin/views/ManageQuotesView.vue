<!--
 * FILENAME: website/js/admin/views/ManageQuotesView.vue
 * UPDATED: Fully implemented to display quote requests.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header><h1 class="text-3xl font-bold text-gray-800">Manage Quotes</h1></header>
      <div v-if="marketingStore.isLoading" class="text-center py-10">Loading quotes...</div>
      <div v-else-if="marketingStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ marketingStore.error }}</div>
      <BaseDataTable v-else :columns="columns" :data="marketingStore.quotes" />
    </div>
  </AdminLayout>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminMarketingStore } from '../../stores/adminMarketing';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const marketingStore = useAdminMarketingStore();
const columns = [ { key: 'id', label: 'ID' }, { key: 'company_name', label: 'Company' }, { key: 'status', label: 'Status' } ];
onMounted(() => { marketingStore.fetchQuotes(); });
</script>
