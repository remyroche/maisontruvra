<!--
 * FILENAME: website/js/admin/views/ManageInventoryView.vue
 * UPDATED: Fully implemented with data table and inline stock editing.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header>
        <h1 class="text-3xl font-bold text-gray-800">Manage Inventory</h1>
        <p class="text-gray-500 mt-1">View and update stock levels for all products.</p>
      </header>
       <div v-if="inventoryStore.isLoading" class="text-center py-10">Loading inventory...</div>
       <div v-else-if="inventoryStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ inventoryStore.error }}</div>
      <BaseDataTable v-else :columns="columns" :data="inventoryStore.inventory">
        <template #cell(stock_quantity)="{ item }">
          <input type="number" :value="item.stock_quantity" @change="handleStockUpdate(item.id, $event.target.value)"
                 class="w-24 text-center border-gray-300 rounded-md shadow-sm" />
        </template>
      </BaseDataTable>
    </div>
  </AdminLayout>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminInventoryStore } from '../../stores/adminInventory';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const inventoryStore = useAdminInventoryStore();
const notificationStore = useAdminNotificationStore();

const columns = [
    { key: 'id', label: 'Product ID'},
    { key: 'name', label: 'Product Name'},
    { key: 'sku', label: 'SKU'},
    { key: 'stock_quantity', label: 'Stock Level'}
];

onMounted(() => { inventoryStore.fetchInventory(); });

const handleStockUpdate = async (id, newStock) => {
    const success = await inventoryStore.updateStock(id, parseInt(newStock, 10));
    if(success) {
        notificationStore.addNotification({ type: 'success', title: 'Stock Updated'});
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Update Failed', message: inventoryStore.error });
        // Optional: refresh data to revert optimistic update on failure
        inventoryStore.fetchInventory();
    }
};
</script>
