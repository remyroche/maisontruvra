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
      <button @click="openCreateModal" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
        Add Product
      </button>
    </div>

    <div v-if="productsStore.isLoading" class="text-center p-4">Loading products...</div>
    <div v-if="productsStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ productsStore.error }}</div>

    <BaseDataTable
      v-if="!productsStore.isLoading && filteredProducts.length"
      :headers="headers"
      :items="filteredProducts"
    >
      <template #item-price="{ item }">
        <span>${{ item.price.toFixed(2) }}</span>
      </template>
      <template #item-is_published="{ item }">
        <span :class="item.is_published ? 'text-green-500' : 'text-gray-500'">
          {{ item.is_published ? 'Published' : 'Draft' }}
        </span>
      </template>
      <template #item-actions="{ item }">
        <button @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
        <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900">Delete</button>
      </template>
    </BaseDataTable>
    <div v-if="!productsStore.isLoading && !filteredProducts.length" class="text-center text-gray-500 mt-8">
        No products found.
    </div>

    <!-- Modal for Create/Edit Product -->
    <Modal :is-open="isModalOpen" @close="closeModal">
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit Product' : 'Create New Product' }}</h2>
        <ProductForm 
            :product="selectedProduct" 
            @save="handleSaveProduct"
            @cancel="closeModal"
        />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminProductsStore } from '@/js/stores/adminProducts';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';
import ProductForm from '@/js/admin/components/ProductForm.vue';

const productsStore = useAdminProductsStore();

const searchQuery = ref('');
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

onMounted(() => {
  productsStore.fetchProducts();
});

const filteredProducts = computed(() => {
  if (!searchQuery.value) {
    return productsStore.products;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return productsStore.products.filter(product => 
    product.name.toLowerCase().includes(lowerCaseQuery) ||
    (product.sku && product.sku.toLowerCase().includes(lowerCaseQuery))
  );
});

const openCreateModal = () => {
    isEditing.value = false;
    selectedProduct.value = { name: '', description: '', price: 0, sku: '', category_id: null, collection_id: null, is_published: true, images: [] };
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
    if (isEditing.value) {
        await productsStore.updateProduct(productData.id, productData);
    } else {
        await productsStore.createProduct(productData);
    }
    closeModal();
};

const confirmDelete = (product) => {
    if (window.confirm(`Are you sure you want to delete the product "${product.name}"?`)) {
        productsStore.deleteProduct(product.id);
    }
};
</script>
