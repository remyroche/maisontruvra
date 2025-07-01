<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <form @submit.prevent="submitForm">
      <div class="space-y-4">
        <h3 class="text-lg font-semibold border-b pb-2">Items for Quote</h3>
        
        <!-- Loop through existing items -->
        <div v-for="(item, index) in quoteItems" :key="index" class="p-4 border rounded-md flex items-start space-x-4">
          <div class="flex-grow space-y-2">
            <div v-if="item.type === 'product'">
              <label class="block text-sm font-medium">Standard Product</label>
              <select v-model="item.product_id" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                <option disabled value="">Select a product</option>
                <option v-for="product in availableProducts" :key="product.id" :value="product.id">
                  {{ product.name }}
                </option>
              </select>
            </div>
            <div v-if="item.type === 'custom'">
              <label class="block text-sm font-medium">Custom Item Name</label>
              <input type="text" v-model="item.custom_item_name" placeholder="e.g., Custom Truffle Salt Blend" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              <label class="block text-sm font-medium mt-2">Custom Item Description</label>
              <textarea v-model="item.custom_item_description" rows="2" placeholder="Describe the item, including specifications, packaging, etc." class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
            </div>
             <div>
              <label class="block text-sm font-medium">Quantity</label>
              <input type="number" v-model.number="item.quantity" min="1" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
          </div>
          <button @click.prevent="removeItem(index)" class="text-red-500 hover:text-red-700 mt-1">&times;</button>
        </div>

        <!-- Add Item Buttons -->
        <div class="flex space-x-4 pt-4">
          <button @click.prevent="addItem('product')" class="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300">Add Standard Product</button>
          <button @click.prevent="addItem('custom')" class="bg-brand-dark-brown text-white py-2 px-4 rounded-md hover:bg-opacity-90">Add Custom Item</button>
        </div>
      </div>

      <div class="mt-8">
        <button type="submit" class="w-full bg-brand-burgundy text-white py-3 px-4 rounded-md hover:bg-opacity-90 transition-colors">
          Submit Quote Request
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProductStore } from '@/stores/products';

const emit = defineEmits(['submit-quote']);
const productStore = useProductStore();

const availableProducts = ref([]);
const quoteItems = ref([]);

onMounted(async () => {
  await productStore.fetchProducts();
  availableProducts.value = productStore.products;
});

const addItem = (type) => {
  if (type === 'product') {
    quoteItems.value.push({ type: 'product', product_id: '', quantity: 1 });
  } else {
    quoteItems.value.push({ type: 'custom', custom_item_name: '', custom_item_description: '', quantity: 1 });
  }
};

const removeItem = (index) => {
  quoteItems.value.splice(index, 1);
};

const submitForm = () => {
  // Filter out any empty items before submitting
  const payload = quoteItems.value.filter(item => 
    (item.type === 'product' && item.product_id) || 
    (item.type === 'custom' && item.custom_item_name)
  ).map(item => {
    const { type, ...rest } = item; // remove the 'type' property
    return rest;
  });

  if (payload.length > 0) {
    emit('submit-quote', { items: payload });
  } else {
    alert("Please add at least one item to the quote.");
  }
};
</script>
