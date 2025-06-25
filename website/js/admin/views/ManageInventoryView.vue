<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Inventory</h1>
    <div v-if="inventoryStore.error" class="text-red-500">{{ inventoryStore.error }}</div>
    <div v-else>
      <table class="min-w-full bg-white">
        <thead>
          <tr>
            <th class="py-2">Product</th>
            <th class="py-2">Stock</th>
            <th class="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventoryStore.inventory" :key="item.id">
            <td class="border px-4 py-2">{{ item.name }}</td>
            <td class="border px-4 py-2">{{ item.stock }}</td>
            <td class="border px-4 py-2">
              <input type="number" v-model.number="item.newStock" class="border rounded p-1" />
              <button @click="updateStock(item.id, item.newStock)" class="bg-blue-500 text-white px-2 py-1 rounded ml-2">Update</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminInventoryStore } from '@/js/stores/adminInventory';

const inventoryStore = useAdminInventoryStore();

onMounted(() => {
  inventoryStore.fetchInventory();
});

const updateStock = (productId, newStock) => {
  if (newStock !== undefined && newStock >= 0) {
    inventoryStore.updateStock(productId, newStock);
  }
};
</script>
