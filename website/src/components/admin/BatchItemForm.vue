<!-- website/src/components/admin/BatchItemForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="space-y-6 bg-white p-6 rounded-lg">
    <h2 class="text-xl font-semibold text-gray-800">Create Item Batch</h2>
    
    <!-- Step 1: Select Parent Product -->
    <div>
      <label for="parentProduct" class="block text-sm font-medium text-gray-700">Parent Product (SKU)</label>
      <select id="parentProduct" v-model="batchData.product_id" @change="onProductSelect" required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        <option disabled value="">Please select a product</option>
        <option v-for="product in products" :key="product.id" :value="product.id">
          {{ product.name }} - ({{ product.sku }})
        </option>
      </select>
    </div>

    <!-- The rest of the form is disabled until a parent product is selected -->
    <fieldset :disabled="!batchData.product_id" class="space-y-6 border-t border-gray-200 pt-6">
      <legend class="text-base font-medium text-gray-900">Batch Details</legend>
      <p v-if="!batchData.product_id" class="text-sm text-gray-500">Select a parent product to continue.</p>

      <!-- Batch-specific fields -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label for="number_to_create" class="block text-sm font-medium text-gray-700">Number of Items to Create</label>
          <input type="number" id="number_to_create" v-model.number="batchData.number_to_create" required min="1" max="100"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
        <div>
          <label for="harvest_date" class="block text-sm font-medium text-gray-700">Harvest Date (Optional)</label>
          <input type="date" id="harvest_date" v-model="batchData.harvest_date"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
      </div>
      
      <!-- Optional Collection -->
      <div>
        <label for="collection" class="block text-sm font-medium text-gray-700">Assign to Collection (Optional)</label>
        <select id="collection" v-model="batchData.collection_id"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
          <option :value="null">No collection</option>
          <option v-for="collection in collections" :key="collection.id" :value="collection.id">
            {{ collection.name }}
          </option>
        </select>
      </div>

       <p class="text-sm text-gray-600">
        Note: All items in this batch will inherit their price, producer notes, and pairing suggestions from the parent product. To set these individually, please use the "Add New Item" button.
      </p>

    </fieldset>

    <div class="flex justify-end pt-4">
      <button type="button" @click="$emit('cancel')" class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
        Cancel
      </button>
      <button type="submit" :disabled="!batchData.product_id" class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
        Create Batch
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminProductStore } from '@/stores/adminProducts';
import { useAdminCollectionStore } from '@/stores/adminCollections';

const emit = defineEmits(['submit', 'cancel']);

const productStore = useAdminProductStore();
const collectionStore = useAdminCollectionStore();

const products = computed(() => productStore.products);
const collections = computed(() => collectionStore.collections);

const batchData = ref({
  product_id: '',
  collection_id: null,
  number_to_create: 10,
  harvest_date: null,
  creation_date: new Date().toISOString().slice(0, 10), // Set creation date for all items in batch
});

const onProductSelect = () => {
  // Logic can be added here if needed when a product is selected
};

const handleSubmit = () => {
  const payload = { ...batchData.value };
  if (payload.harvest_date === '') delete payload.harvest_date;
  if (payload.collection_id === '') payload.collection_id = null;
  
  emit('submit', payload);
};

onMounted(() => {
  productStore.fetchAllProducts();
  collectionStore.fetchAllCollections();
});
</script>
