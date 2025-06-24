<!--
 * FILENAME: website/js/admin/views/ViewPassportsView.vue
 * UPDATED: Implemented to display a list of generated product passports.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header><h1 class="text-3xl font-bold text-gray-800">View Product Passports</h1></header>
       <div v-if="systemStore.isLoading" class="text-center py-10">Loading passports...</div>
      <div v-else-if="systemStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ systemStore.error }}</div>
      <BaseDataTable v-else :columns="columns" :data="systemStore.passports">
          <template #cell(actions)="{ item }">
              <a :href="`/api/admin/passports/${item.id}/download`" target="_blank" class="bg-blue-500 text-white font-bold py-1 px-2 rounded text-xs">Download</a>
          </template>
      </BaseDataTable>
    </div>
  </AdminLayout>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminSystemStore } from '../../stores/adminSystem';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const systemStore = useAdminSystemStore();
const columns = [ { key: 'product_name', label: 'Product' }, { key: 'created_at', label: 'Date Generated'}, { key: 'actions', label: 'Actions'} ];
onMounted(() => { systemStore.fetchPassports(); });
</script>
