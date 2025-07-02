<!-- website/src/components/admin/ItemForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="space-y-6 bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-semibold text-gray-800">Create New Inventory Item</h2>
    
    <!-- Step 1: Select Parent Product -->
    <div>
      <label for="parentProduct" class="block text-sm font-medium text-gray-700">Parent Product (SKU)</label>
      <select id="parentProduct" v-model="selectedProductId" @change="onProductSelect"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        <option disabled value="">Please select a product</option>
        <option v-for="product in products" :key="product.id" :value="product.id">
          {{ product.name }} - ({{ product.sku }})
        </option>
      </select>
    </div>

    <!-- The rest of the form is disabled until a parent product is selected -->
    <fieldset :disabled="!selectedProduct" class="space-y-6 border-t border-gray-200 pt-6">
      <legend class="text-base font-medium text-gray-900">Item Details</legend>
      <p v-if="!selectedProduct" class="text-sm text-gray-500">Select a parent product to continue.</p>

      <!-- Item-specific fields -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label for="stock_quantity" class="block text-sm font-medium text-gray-700">Stock Quantity</label>
          <input type="number" id="stock_quantity" v-model.number="itemData.stock_quantity" required
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
        <div>
          <label for="creation_date" class="block text-sm font-medium text-gray-700">Creation Date</label>
          <input type="date" id="creation_date" v-model="itemData.creation_date" required
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
        <div>
          <label for="harvest_date" class="block text-sm font-medium text-gray-700">Harvest Date (Optional)</label>
          <input type="date" id="harvest_date" v-model="itemData.harvest_date"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
      </div>
      
      <!-- Optional Collection -->
      <div>
        <label for="collection" class="block text-sm font-medium text-gray-700">Assign to Collection (Optional)</label>
        <select id="collection" v-model="itemData.collection_id"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
          <option :value="null">No collection</option>
          <option v-for="collection in collections" :key="collection.id" :value="collection.id">
            {{ collection.name }}
          </option>
        </select>
      </div>

      <!-- Overridable Fields -->
      <div class="space-y-6 border-t border-gray-200 pt-6">
        <h3 class="text-base font-medium text-gray-900">Override Information (Optional)</h3>
        <p class="text-sm text-gray-500">Leave fields blank to use the information from the parent product.</p>
        
        <div>
          <label for="price_override" class="block text-sm font-medium text-gray-700">Price Override (€)</label>
          <input type="number" step="0.01" id="price_override" v-model.number="itemData.price"
                 :placeholder="`Default: ${formatCurrency(selectedProduct?.price || 0)}`"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
        </div>
        
        <div>
          <label for="producer_notes_override" class="block text-sm font-medium text-gray-700">Producer's Notes Override</label>
          <textarea id="producer_notes_override" v-model="itemData.producer_notes" rows="3"
                    :placeholder="`Default: ${selectedProduct?.producer_notes || 'Not set'}`"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
        </div>
        
        <div>
          <label for="pairing_suggestions_override" class="block text-sm font-medium text-gray-700">Pairing Suggestions Override</label>
          <textarea id="pairing_suggestions_override" v-model="itemData.pairing_suggestions" rows="3"
                    :placeholder="`Default: ${selectedProduct?.pairing_suggestions || 'Not set'}`"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
        </div>
      </div>
    </fieldset>

    <div class="flex justify-end pt-4">
      <button type="button" @click="$emit('cancel')" class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
        Cancel
      </button>
      <button type="submit" :disabled="!selectedProduct" class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
        Create Item
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminProductStore } from '@/stores/adminProducts'; // Assuming this store exists
import { useAdminCollectionStore } from '@/stores/adminCollections'; // Assuming this store exists
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';

const emit = defineEmits(['submit', 'cancel']);

const productStore = useAdminProductStore();
const collectionStore = useAdminCollectionStore();
const { formatCurrency } = useCurrencyFormatter();

// Data for the dropdowns
const products = computed(() => productStore.products);
const collections = computed(() => collectionStore.collections);

const selectedProductId = ref('');
const selectedProduct = ref(null);

// Form data for the new item
const itemData = ref({
  product_id: null,
  collection_id: null,
  stock_quantity: 1,
  creation_date: new Date().toISOString().slice(0, 10), // Defaults to today
  harvest_date: null, // <-- NEW FIELD
  price: null, // Null means use parent's price
  producer_notes: null,
  pairing_suggestions: null,
});

const onProductSelect = () => {
  selectedProduct.value = products.value.find(p => p.id === selectedProductId.value);
  if (selectedProduct.value) {
    itemData.value.product_id = selectedProduct.value.id;
  }
};

const handleSubmit = () => {
  // Create a clean payload, removing null/empty values so the backend uses the parent's data
  const payload = { ...itemData.value };
  if (payload.price === '' || payload.price === null) delete payload.price;
  if (payload.producer_notes === '' || payload.producer_notes === null) delete payload.producer_notes;
  if (payload.pairing_suggestions === '' || payload.pairing_suggestions === null) delete payload.pairing_suggestions;
  if (payload.harvest_date === '' || payload.harvest_date === null) delete payload.harvest_date;
  
  emit('submit', payload);
};

onMounted(() => {
  // Fetch necessary data for the form dropdowns
  productStore.fetchAllProducts();
  collectionStore.fetchAllCollections();
});
</script>
