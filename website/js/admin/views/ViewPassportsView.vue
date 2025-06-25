<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Product Passports</h1>
    <BaseDataTable v-if="!passportsStore.isLoading" :headers="headers" :items="passportsStore.passports">
      <template #item-actions="{ item }">
        <button @click="download(item.id)" class="text-indigo-600 hover:text-indigo-900">Download PDF</button>
      </template>
    </BaseDataTable>
    <div v-else>Loading passports...</div>
  </div>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminPassportsStore } from '@/js/stores/adminPassports';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const passportsStore = useAdminPassportsStore();
const headers = [
    { text: 'Passport ID', value: 'id' },
    { text: 'Product Name', value: 'product_name' },
    { text: 'Date Generated', value: 'created_at' },
    { text: 'Actions', value: 'actions' },
];

onMounted(() => passportsStore.fetchPassports());
const download = (id) => passportsStore.downloadPassport(id);
</script>
