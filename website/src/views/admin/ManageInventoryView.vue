<template>
  <div>
    <h1>Inventory Management</h1>
    <div v-if="inventoryStore.loading" class="loading-state">Loading inventory...</div>
    <div v-if="inventoryStore.error" class="error-state">{{ inventoryStore.error }}</div>
    
    <table v-if="!inventoryStore.loading && inventory.length" class="inventory-table">
      <thead>
        <tr>
          <th>Product Name</th>
          <th>SKU</th>
          <th>Current Stock</th>
          <th>New Stock</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in inventory" :key="item.product_id">
          <td>{{ item.product_name }}</td>
          <td>{{ item.sku }}</td>
          <td>{{ item.stock_level }}</td>
          <td>
            <Field 
              :name="`stock_${item.product_id}`" 
              type="number" 
              class="stock-input"
              v-model="item.new_stock"
              :rules="isNonNegativeInteger"
            />
            <ErrorMessage :name="`stock_${item.product_id}`" class="error-message" />
          </td>
          <td>
            <button 
              @click="handleUpdateStock(item.product_id, item.new_stock)" 
              class="update-button"
              :disabled="isUpdating[item.product_id]">
              <span v-if="isUpdating[item.product_id]">...</span>
              <span v-else>Update</span>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAdminInventoryStore } from '@/stores/adminInventory';
import { Field, ErrorMessage } from 'vee-validate';
import { isNonNegativeInteger } from '@/validation/rules';
import { storeToRefs } from 'pinia';

const inventoryStore = useAdminInventoryStore();
const { inventory } = storeToRefs(inventoryStore);

const isUpdating = ref({});

onMounted(() => {
  inventoryStore.fetchInventory();
});

const handleUpdateStock = async (productId, newStock) => {
  // Client-side validation before sending
  if (isNonNegativeInteger(newStock) !== true) {
    alert('Please enter a valid, non-negative integer for the stock.');
    return;
  }
  
  isUpdating.value[productId] = true;
  try {
    await inventoryStore.updateStock(productId, parseInt(newStock, 10));
    // Optionally show a success notification
  } catch(error) {
    // Optionally show an error notification
    alert('Failed to update stock.');
  } finally {
    isUpdating.value[productId] = false;
  }
};
</script>

<style scoped>
.inventory-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.inventory-table th, .inventory-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
.stock-input {
  width: 80px;
  padding: 4px;
}
.update-button {
  padding: 5px 10px;
  cursor: pointer;
}
.update-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.error-message {
  color: #e53e3e;
  font-size: 0.875rem;
}
</style>
