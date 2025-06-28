<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Products</h1>
    
    <div class="mb-4 flex justify-between items-center">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by name or SKU..." 
        class="border rounded p-2 w-1/3"
      >
      <div class="flex items-center space-x-4">
        <label class="flex items-center text-sm">
            <input type="checkbox" v-model="includeDeleted" class="mr-2 h-4 w-4 rounded">
            Show Deleted
        </label>
        <button @click="openCreateModal" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
          Add Product
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="text-center p-4">Loading products...</div>
    <div v-else-if="error" class="text-red-500 bg-red-100 p-4 rounded">Failed to load products. Please try again.</div>

    <BaseDataTable
      v-else-if="productsData && productsData.data.length"
      :headers="headers"
      :items="productsData.data"
    >
        <template #row="{ item }">
            <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                <td class="px-6 py-4 whitespace-nowrap text-sm">{{ item.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">{{ item.sku }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">€{{ item.price.toFixed(2) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">{{ item.category?.name || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span :class="item.is_published ? 'text-green-500' : 'text-gray-500'">
                        {{ item.is_published ? 'Published' : 'Draft' }}
                    </span>
                    <span v-if="item.is_deleted" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-200 text-red-800">Deleted</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <div class="flex items-center space-x-2">
                        <button v-if="!item.is_deleted" @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900">Edit</button>
                        <button v-if="!item.is_deleted" @click="confirmDelete(item, 'soft')" class="text-yellow-600 hover:text-yellow-900">Soft Delete</button>
                        <button v-if="item.is_deleted" @click="restoreProduct(item.id)" class="text-green-600 hover:text-green-900">Restore</button>
                        <button @click="confirmDelete(item, 'hard')" class="text-red-600 hover:text-red-900">Hard Delete</button>
                    </div>
                </td>
            </tr>
        </template>
    </BaseDataTable>
    <div v-else class="text-center text-gray-500 mt-8">
        No products found.
    </div>

    <!-- Add pagination controls here -->

    <Modal :show="isModalOpen" @close="closeModal">
        <template #header>
            <h2 class="text-xl font-bold">{{ isEditing ? 'Edit Product' : 'Create New Product' }}</h2>
        </template>
        <template #body>
            <ProductForm 
                :product="selectedProduct" 
                @save="handleSaveProduct"
                @cancel="closeModal"
            />
        </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useDebounce } from '@vueuse/core';
import { useApiData } from '@/composables/useApiData';
import { useAdminProductsStore } from '@/stores/adminProducts';
import { adminApiClient } from '@/services/api';
import BaseDataTable from '@/components/admin/ui/BaseDataTable.vue';
import Modal from '@/components/admin/ui/Modal.vue';
import ProductForm from '@/components/admin/products/ProductForm.vue';

const productsStore = useAdminProductsStore();

const searchQuery = ref('');
const debouncedSearchQuery = useDebounce(searchQuery, 300); // Debounce input by 300ms
const includeDeleted = ref(false);
const currentPage = ref(1);

const isModalOpen = ref(false);
const isEditing = ref(false);
const selectedProduct = ref(null);

const headers = [
  { text: 'Name', value: 'name' },
  { text: 'SKU', value: 'sku' },
  { text: 'Price', value: 'price' },
  { text: 'Category', value: 'category.name' },
  { text: 'Status', value: 'is_published' },
  { text: 'Actions', value: 'actions', sortable: false },
];

const apiUrl = computed(() => {
    const params = new URLSearchParams();
    params.append('page', currentPage.value);
    params.append('per_page', 20);
    if (debouncedSearchQuery.value) {
        params.append('search', debouncedSearchQuery.value);
    }
    if (includeDeleted.value) {
        params.append('include_deleted', 'true');
    }
    return `/products?${params.toString()}`;
});

const { data: productsData, isLoading, error, fetchData } = useApiData(
    () => adminApiClient.get(apiUrl.value),
    apiUrl // Watch the computed URL to refetch automatically
);

const openCreateModal = () => {
    isEditing.value = false;
    selectedProduct.value = { name: '', description: '', price: 0, sku: '', category_id: null, is_published: true };
    isModalOpen.value = true;
};

const openEditModal = (product) => {
    isEditing.value = true;
    selectedProduct.value = { ...product };
    isModalOpen.value = true;
};

const closeModal = () => {
    isModalOpen.value = false;
    selectedProduct.value = null;
};

const handleSaveProduct = async (productData) => {
    const success = isEditing.value
        ? await productsStore.updateProduct(productData.id, productData)
        : await productsStore.createProduct(productData);
    if (success) {
        closeModal();
        fetchData(); // Re-fetch the list to show changes
    }
};

const confirmDelete = async (product, type) => {
    const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
    if (window.confirm(`Are you sure you want to ${action} the product "${product.name}"?`)) {
        const success = type === 'soft'
            ? await productsStore.softDeleteProduct(product.id)
            : await productsStore.hardDeleteProduct(product.id);
        if (success) {
            fetchData(); // Re-fetch the list
        }
    }
};

const restoreProduct = async (productId) => {
    if (window.confirm('Are you sure you want to restore this product?')) {
        const success = await productsStore.restoreProduct(productId);
        if (success) {
            fetchData(); // Re-fetch the list
        }
    }
};
</script>