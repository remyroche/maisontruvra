<template>
  <form @submit.prevent="submitForm" class="p-4">
    <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit' : 'Add' }} Collection</h2>
    <div class="mb-4">
      <label for="name" class="block text-sm font-medium text-gray-700">Collection Name</label>
      <input type="text" id="name" v-model="form.name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
    </div>
    <div class="mb-4">
      <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
      <textarea id="description" v-model="form.description" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
    </div>
    <div class="mb-4">
        <h3 class="block text-sm font-medium text-gray-700 mb-2">Products in this Collection</h3>
        <div class="max-h-60 overflow-y-auto border rounded-md p-2">
            <div v-for="product in allProducts" :key="product.id">
                <label class="flex items-center space-x-2">
                    <input type="checkbox" :value="product.id" v-model="form.product_ids" class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-offset-0 focus:ring-indigo-200 focus:ring-opacity-50">
                    <span>{{ product.name }}</span>
                </label>
            </div>
        </div>
         <p v-if="loading" class="text-sm text-gray-500">Loading products...</p>
         <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
    </div>
    <div class="flex justify-end space-x-2">
      <button type="button" @click="$emit('cancel')" class="px-4 py-2 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300">Cancel</button>
      <button type="submit" class="px-4 py-2 rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 border border-transparent">Save</button>
    </div>
  </form>
</template>

<script>
import { ref, watch, computed, onMounted } from 'vue';
import api from '@/services/api';

export default {
  name: 'CollectionForm',
  props: {
    collection: {
      type: Object,
      default: () => ({ product_ids: [] }),
    },
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const form = ref({ product_ids: [] });
    const allProducts = ref([]);
    const loading = ref(false);
    const error = ref(null);

    const isEditing = computed(() => !!(form.value && form.value.id));

    watch(() => props.collection, (newVal) => {
      form.value = { ...newVal, product_ids: newVal.product_ids || [] };
    }, { immediate: true, deep: true });

    onMounted(async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await api.get('/admin/products'); // Assuming an endpoint to fetch all products
            allProducts.value = response.data.products || response.data;
        } catch (e) {
            console.error("Failed to fetch products for collection form", e);
            error.value = "Could not load products.";
        } finally {
            loading.value = false;
        }
    });

    const submitForm = () => {
      emit('save', form.value);
    };

    return {
      form,
      isEditing,
      allProducts,
      loading,
      error,
      submitForm,
    };
  },
};
</script>