<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Product Passports</h1>
    <BaseDataTable :columns="columns" :data="passports" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
// Corrected the import path for BaseDataTable
import BaseDataTable from '@/components/ui/BaseDataTable.vue';
import api from '@/services/api';

export default {
  name: 'ViewPassportsView',
  components: {
    BaseDataTable,
  },
  setup() {
    const passports = ref([]);
    const columns = [
      { key: 'product_name', label: 'Product' },
      { key: 'passport_id', label: 'Passport ID' },
      { key: 'creation_date', label: 'Date Created' },
    ];

    onMounted(async () => {
      try {
        const response = await api.get('/admin/passports');
        passports.value = response.data;
      } catch (error) {
        console.error('Failed to fetch passports:', error);
      }
    });

    return {
      passports,
      columns,
    };
  },
};
</script>