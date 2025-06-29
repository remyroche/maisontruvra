<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Product Categories</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="md:col-span-2">
         <BaseDataTable :headers="headers" :items="categoriesStore.categories">
            <template #row="{ item, children }">
                <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                    <td v-for="header in headers" :key="header.value" class="px-6 py-4 whitespace-nowrap text-sm">
                        <slot :name="`item-${header.value}`" :item="item">{{ getNestedValue(item, header.value) }}</slot>
                    </td>
                </tr>
            </template>
             <template #item-actions="{ item }">
                <div class="flex items-center space-x-2">
                    <button v-if="!item.is_deleted" @click="openModal(item)" class="text-indigo-600 hover:text-indigo-900 text-sm">Edit</button>
                    <button v-if="!item.is_deleted" @click="deleteCategory(item.id, 'soft')" class="text-yellow-600 hover:text-yellow-900 text-sm">Soft Delete</button>
                    <button v-if="item.is_deleted" @click="restoreCategory(item.id)" class="text-green-600 hover:text-green-900 text-sm">Restore</button>
                    <button @click="deleteCategory(item.id, 'hard')" class="text-red-600 hover:text-red-900 text-sm">Hard Delete</button>
                </div>
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
import CategoryForm from '@/components/admin/CategoryForm.vue';

const categoriesStore = useAdminCategoriesStore();
const isEditing = ref(false);
const selectedCategory = ref({ name: '', description: '' });
const formKey = ref(0);

const headers = [
    { text: 'Name', value: 'name' },
    { text: 'Description', value: 'description' },
    { text: 'Actions', value: 'actions' },
];

const getNestedValue = (item, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], item);
}

onMounted(() => categoriesStore.fetchCategories({ include_deleted: true }));

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

const deleteCategory = (id, type) => {
    const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
    if(confirm(`Are you sure you want to ${action} this category? Deleting a category may affect products.`)) {
        const deleteAction = type === 'soft' ? categoriesStore.softDeleteCategory : categoriesStore.hardDeleteCategory;
        deleteAction(id);
    }
};

const restoreCategory = (id) => {
    if(confirm('Are you sure you want to restore this category?')) {
        categoriesStore.restoreCategory(id);
    }
}
</script>
