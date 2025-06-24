<!--
 * FILENAME: website/js/admin/components/ProductForm.vue
 * DESCRIPTION: A form for creating or editing product details.
 *
 * This component is used inside a modal for product data entry, featuring
 * fields for name, price, stock, description, and associations.
-->
<template>
  <form @submit.prevent="handleSubmit">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Name -->
      <div class="md:col-span-2">
        <label for="name" class="block text-sm font-medium text-gray-700">Product Name</label>
        <input type="text" id="name" v-model="formData.name" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>

      <!-- Price & Stock -->
      <div>
        <label for="price" class="block text-sm font-medium text-gray-700">Price (€)</label>
        <input type="number" step="0.01" id="price" v-model.number="formData.price" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>
      <div>
        <label for="stock" class="block text-sm font-medium text-gray-700">Stock Quantity</label>
        <input type="number" id="stock" v-model.number="formData.stock_quantity" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>

      <!-- Category & Collection -->
      <div>
        <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
        <select id="category" v-model="formData.category_id" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
          <option :value="null">-- Select a category --</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <div>
        <label for="collection" class="block text-sm font-medium text-gray-700">Collection</label>
        <select id="collection" v-model="formData.collection_id" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
           <option :value="null">-- Select a collection --</option>
          <option v-for="col in collections" :key="col.id" :value="col.id">{{ col.name }}</option>
        </select>
      </div>

      <!-- Description -->
      <div class="md:col-span-2">
        <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea id="description" v-model="formData.description" rows="4" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
      </div>
       <!-- Is Active -->
      <div class="md:col-span-2">
        <label class="flex items-center">
            <input type="checkbox" v-model="formData.is_active" class="h-4 w-4 text-indigo-600 rounded">
            <span class="ml-2 text-sm text-gray-900">Product is Active</span>
        </label>
      </div>
    </div>
    
    <div class="mt-6 flex justify-end space-x-3">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
      <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">{{ isEditing ? 'Update' : 'Create' }}</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  initialData: Object,
  categories: Array,
  collections: Array,
});

const emit = defineEmits(['submit', 'cancel']);

const formData = ref({ ...props.initialData });
const isEditing = computed(() => !!props.initialData?.id);

watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true, immediate: true });

const handleSubmit = () => {
  emit('submit', JSON.parse(JSON.stringify(formData.value)));
};
</script>
