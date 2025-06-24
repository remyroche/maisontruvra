<!--
 * FILENAME: website/js/admin/views/ManageProductsView.vue
 * DESCRIPTION: View component for the 'Manage Products' page.
 *
 * This component orchestrates the display and management of products,
 * using the reusable Modal component and the new ProductForm.
-->
<template>
  <AdminLayout>
    <div class="bg-white p-8 rounded-lg shadow-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Manage Products</h1>
        <button @click="openAddProductModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add Product
        </button>
      </div>

      <!-- Loading and Error States -->
      <div v-if="productStore.isLoading && !productStore.products.length" class="text-center py-10">Loading products...</div>
      <div v-else-if="productStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        {{ productStore.error }}
      </div>

      <!-- Data Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full bg-white">
          <thead class="bg-gray-800 text-white">
            <tr>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">ID</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Name</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Category</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-right">Price</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-right">Stock</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="text-gray-700">
            <tr v-for="product in productStore.products" :key="product.id" class="border-b border-gray-200 hover:bg-gray-100">
              <td class="py-3 px-4">{{ product.id }}</td>
              <td class="py-3 px-4">{{ product.name }}</td>
              <td class="py-3 px-4">{{ product.category?.name || 'N/A' }}</td>
              <td class="py-3 px-4 text-right">€{{ product.price.toFixed(2) }}</td>
              <td class="py-3 px-4 text-right">{{ product.stock_quantity }}</td>
              <td class="py-3 px-4 text-center">
                <button @click="openEditProductModal(product)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                <button @click="handleDeleteProduct(product)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Product Modal -->
    <Modal :show="isModalOpen" @close="closeModal">
      <template #header>
        <h2 class="text-2xl font-bold">{{ modalMode === 'add' ? 'Add New Product' : 'Edit Product' }}</h2>
      </template>
      <template #body>
        <ProductForm 
          :initial-data="currentProduct" 
          :categories="productStore.categories"
          :collections="productStore.collections"
          @submit="handleFormSubmit"
          @cancel="closeModal"
        />
      </template>
       <template #footer><div></div></template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminProductStore } from '../../stores/adminProducts';
import AdminLayout from '../components/AdminLayout.vue';
import Modal from '../components/Modal.vue';
import ProductForm from '../components/ProductForm.vue';

const productStore = useAdminProductStore();

const isModalOpen = ref(false);
const modalMode = ref('add');
const currentProduct = ref({});

onMounted(() => {
  productStore.fetchProductsAndRelatedData();
});

const openAddProductModal = () => {
  modalMode.value = 'add';
  currentProduct.value = { name: '', description: '', price: 0, stock_quantity: 0, category_id: null, collection_id: null, is_active: true };
  isModalOpen.value = true;
};

const openEditProductModal = (product) => {
  modalMode.value = 'edit';
  currentProduct.value = JSON.parse(JSON.stringify(product));
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleFormSubmit = async (productData) => {
  let success = false;
  if (modalMode.value === 'add') {
    success = await productStore.createProduct(productData);
  } else {
    success = await productStore.updateProduct(productData.id, productData);
  }
  
  if (success) {
    closeModal();
  }
};

const handleDeleteProduct = async (product) => {
  if (confirm(`Are you sure you want to delete product "${product.name}"?`)) {
    await productStore.deleteProduct(product.id);
  }
};
</script>
