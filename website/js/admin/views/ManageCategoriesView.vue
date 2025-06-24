<!--
 * FILENAME: website/js/admin/views/ManageCategoriesView.vue
 * DESCRIPTION: View component for the 'Manage Categories' page.
-->
<template>
  <AdminLayout>
    <div class="bg-white p-8 rounded-lg shadow-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Manage Categories</h1>
        <button @click="openAddModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add Category
        </button>
      </div>

      <div v-if="categoryStore.isLoading && !categoryStore.categories.length" class="text-center py-10">Loading categories...</div>
      <div v-else-if="categoryStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        {{ categoryStore.error }}
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full bg-white">
          <thead class="bg-gray-800 text-white">
            <tr>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">ID</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Name</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-left">Description</th>
              <th class="py-3 px-4 uppercase font-semibold text-sm text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="text-gray-700">
            <tr v-for="category in categoryStore.categories" :key="category.id" class="border-b hover:bg-gray-100">
              <td class="py-3 px-4">{{ category.id }}</td>
              <td class="py-3 px-4">{{ category.name }}</td>
              <td class="py-3 px-4">{{ category.description || 'N/A' }}</td>
              <td class="py-3 px-4 text-center">
                <button @click="openEditModal(category)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                <button @click="handleDelete(category)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal :show="isModalOpen" @close="closeModal">
      <template #header>
        <h2 class="text-2xl font-bold">{{ isEditing ? 'Edit Category' : 'Add New Category' }}</h2>
      </template>
      <template #body>
        <CategoryForm :initial-data="currentCategory" @submit="handleSubmit" @cancel="closeModal" />
      </template>
      <template #footer><div></div></template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminCategoryStore } from '../../stores/adminCategories';
import AdminLayout from '../components/AdminLayout.vue';
import Modal from '../components/Modal.vue';
import CategoryForm from '../components/CategoryForm.vue';

const categoryStore = useAdminCategoryStore();

const isModalOpen = ref(false);
const currentCategory = ref({});
const isEditing = computed(() => !!currentCategory.value.id);

onMounted(() => {
  categoryStore.fetchCategories();
});

const openAddModal = () => {
  currentCategory.value = { name: '', description: '' };
  isModalOpen.value = true;
};

const openEditModal = (category) => {
  currentCategory.value = JSON.parse(JSON.stringify(category));
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleSubmit = async (categoryData) => {
  let success = false;
  if (isEditing.value) {
    success = await categoryStore.updateCategory(categoryData.id, categoryData);
  } else {
    success = await categoryStore.createCategory(categoryData);
  }
  if (success) {
    closeModal();
  }
};

const handleDelete = async (category) => {
  if (confirm(`Are you sure you want to delete category "${category.name}"?`)) {
    await categoryStore.deleteCategory(category.id);
  }
};
</script>
