<!-- website/src/views/admin/ManageInventoryView.vue -->
<template>
  <div class="p-4 sm:p-6 lg:p-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-xl font-semibold text-gray-900">Inventory Management</h1>
        <p class="mt-2 text-sm text-gray-700">A list of all unique items in your store, grouped by parent product.</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none space-x-2">
        <button @click="openAddItemModal" type="button" class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
          Add New Item
        </button>
        <button @click="openBatchModal" type="button" class="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50">
          Add Batch
        </button>
      </div>
    </div>

    <!-- Loading and Error States -->
    <div v-if="inventoryStore.loading && !inventoryStore.items.length" class="mt-8 text-center">Loading inventory...</div>
    <div v-if="inventoryStore.error" class="mt-8 text-red-500 text-center">{{ inventoryStore.error }}</div>

    <!-- Inventory List -->
    <div v-else class="mt-8 flex flex-col">
      <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div class="space-y-4">
            <!-- Grouped by Product -->
            <div v-for="group in groupedItems" :key="group.productId" class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <div class="bg-gray-50 px-4 py-3 font-semibold text-gray-800">
                {{ group.productName }} ({{ group.productSku }}) - Total Stock: {{ group.totalStock }}
              </div>
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Item UID</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Creation Date</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Harvest Date</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Stock</th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Price</th>
                    <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6"><span class="sr-only">Edit</span></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-for="item in group.items" :key="item.id">
                    <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-mono text-gray-500 sm:pl-6">{{ item.uid.substring(0, 8) }}...</td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatDate(item.creation_date) }}</td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.harvest_date ? formatDate(item.harvest_date) : 'N/A' }}</td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ item.stock_quantity }}</td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatCurrency(item.price) }}</td>
                    <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <a href="#" class="text-indigo-600 hover:text-indigo-900">Edit<span class="sr-only">, {{ item.uid }}</span></a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Single Item Modal -->
    <Modal :is-open="isItemModalOpen" @close="closeItemModal">
        <template #title>Add New Inventory Item</template>
        <template #content>
            <ItemForm @submit="handleItemSubmit" @cancel="closeItemModal" />
        </template>
    </Modal>
    
    <!-- Add Batch Item Modal -->
    <Modal :is-open="isBatchModalOpen" @close="closeBatchModal">
        <template #title>Add Item Batch</template>
        <template #content>
            <BatchItemForm @submit="handleBatchSubmit" @cancel="closeBatchModal" />
        </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminInventoryStore } from '@/stores/adminInventory';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { useDateFormatter } from '@/composables/useDateFormatter';
import Modal from '@/components/ui/Modal.vue';
import ItemForm from '@/components/admin/ItemForm.vue';
import BatchItemForm from '@/components/admin/BatchItemForm.vue';

const inventoryStore = useAdminInventoryStore();
const { formatCurrency } = useCurrencyFormatter();
const { formatDate } = useDateFormatter();

const isItemModalOpen = ref(false);
const isBatchModalOpen = ref(false);

const groupedItems = computed(() => {
  const groups = {};
  inventoryStore.items.forEach(item => {
    if (!groups[item.product_id]) {
      groups[item.product_id] = {
        productId: item.product_id,
        productName: item.product_name,
        productSku: item.product_sku,
        items: [],
        totalStock: 0,
      };
    }
    groups[item.product_id].items.push(item);
    groups[item.product_id].totalStock += item.stock_quantity;
  });
  return Object.values(groups).sort((a, b) => a.productName.localeCompare(b.productName));
});

const openAddItemModal = () => { isItemModalOpen.value = true; };
const closeItemModal = () => { isItemModalOpen.value = false; };

const openBatchModal = () => { isBatchModalOpen.value = true; };
const closeBatchModal = () => { isBatchModalOpen.value = false; };

const handleItemSubmit = async (itemData) => {
  const success = await inventoryStore.createItem(itemData);
  if (success) {
    closeItemModal();
  }
};

const handleBatchSubmit = async (batchData) => {
  const success = await inventoryStore.createItemBatch(batchData);
  if (success) {
    closeBatchModal();
  }
};

onMounted(() => {
  inventoryStore.fetchAllItems();
});
</script>
