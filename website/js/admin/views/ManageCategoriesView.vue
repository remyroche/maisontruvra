<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Product Categories</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="md:col-span-2">
         <BaseDataTable :headers="headers" :items="categoriesStore.categories">
             <template #item-actions="{ item }">
                 <button @click="openModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
                 <button @click="deleteCategory(item.id)" class="text-red-600 hover:text-red-900">Delete</button>
             </template>
        </BaseDataTable>
      </div>
      <div>
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit Category' : 'New Category' }}</h2>
        <div class="bg-white p-4 rounded shadow">
          <CategoryForm :category="selectedCategory" @save="saveCategory" :key="formKey" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminCategoriesStore } from '@/js/stores/adminCategories';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import CategoryForm from '@/js/admin/components/CategoryForm.vue';

const categoriesStore = useAdminCategoriesStore();
const isEditing = ref(false);
const selectedCategory = ref({ name: '', description: '' });
const formKey = ref(0);

const headers = [
    { text: 'Name', value: 'name' },
    { text: 'Description', value: 'description' },
    { text: 'Actions', value: 'actions' },
];

onMounted(() => categoriesStore.fetchCategories());

const openModal = (category) => {
    isEditing.value = true;
    selectedCategory.value = { ...category };
    formKey.value++; // Force re-render of form
};

const saveCategory = async (data) => {
    if(isEditing.value) {
        await categoriesStore.updateCategory(selectedCategory.value.id, data);
    } else {
        await categoriesStore.createCategory(data);
    }
    isEditing.value = false;
    selectedCategory.value = { name: '', description: '' };
    formKey.value++;
};

const deleteCategory = (id) => {
    if(confirm('Are you sure? Deleting a category may affect products.')) {
        categoriesStore.deleteCategory(id);
    }
};

</script>
