<!--
 * FILENAME: website/js/admin/components/ui/BaseDataTable.vue
 * DESCRIPTION: New powerful, reusable data table component.
-->
<template>
  <div class="overflow-x-auto bg-white rounded-lg shadow">
    <table class="min-w-full">
      <thead class="bg-gray-50">
        <tr>
          <th v-for="column in columns" :key="column.key" 
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="column.headerClass">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200">
        <tr v-if="!data.length">
            <td :colspan="columns.length" class="p-6 text-center text-gray-500">
                No data available.
            </td>
        </tr>
        <tr v-for="(item, index) in data" :key="item.id || index" class="hover:bg-gray-50">
          <td v-for="column in columns" :key="column.key" class="px-6 py-4 whitespace-nowrap text-sm text-gray-700" :class="column.cellClass">
            <!-- Allow custom cell rendering via slots -->
            <slot :name="`cell(${column.key})`" :item="item" :value="item[column.key]">
              <!-- Default cell content -->
              {{ item[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  columns: {
    type: Array,
    required: true, // e.g., [{ key: 'id', label: 'ID' }, { key: 'name', label: 'Name' }]
  },
  data: {
    type: Array,
    required: true,
  },
});
</script>
