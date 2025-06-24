<!--
 * FILENAME: website/js/admin/views/ManageBlogView.vue
 * DESCRIPTION: View for managing blog content, now fully implemented with a tabbed interface.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header>
        <h1 class="text-3xl font-bold text-gray-800">Manage Blog</h1>
      </header>

      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button @click="activeTab = 'articles'" :class="[activeTab === 'articles' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300']" class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm">
            Articles
          </button>
          <button @click="activeTab = 'categories'" :class="[activeTab === 'categories' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300']" class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm">
            Categories
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div v-if="blogStore.isLoading" class="text-center py-10">Loading...</div>
      <div v-else-if="blogStore.error" class="bg-red-100 p-4 rounded-md text-red-700">{{ blogStore.error }}</div>
      
      <!-- Articles Tab -->
      <div v-show="activeTab === 'articles'">
        <div class="flex justify-end mb-4">
            <button @click="openModal('addArticle')" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">+ Add Article</button>
        </div>
        <BaseDataTable :columns="articleColumns" :data="blogStore.articles">
            <template #cell(is_published)="{ value }">
                <span :class="value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">{{ value ? 'Published' : 'Draft' }}</span>
            </template>
            <template #cell(actions)="{ item }">
                <button @click="openModal('editArticle', item)" class="bg-yellow-500 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                <button @click="handleDelete('article', item)" class="bg-red-500 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
            </template>
        </BaseDataTable>
      </div>
      
      <!-- Categories Tab -->
       <div v-show="activeTab === 'categories'">
        <div class="flex justify-end mb-4">
            <button @click="openModal('addCategory')" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">+ Add Category</button>
        </div>
        <BaseDataTable :columns="categoryColumns" :data="blogStore.categories">
            <template #cell(actions)="{ item }">
                <button @click="openModal('editCategory', item)" class="bg-yellow-500 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                <button @click="handleDelete('category', item)" class="bg-red-500 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
            </template>
        </BaseDataTable>
      </div>
    </div>

    <!-- Modal for Forms -->
    <Modal :show="isModalOpen" @close="closeModal">
        <template #header><h2 class="text-2xl font-bold">{{ modalTitle }}</h2></template>
        <template #body>
            <BlogArticleForm v-if="modalMode.startsWith('Article')" :initial-data="currentItem" :categories="blogStore.categories" @submit="handleSubmit" @cancel="closeModal" />
            <BlogCategoryForm v-if="modalMode.startsWith('Category')" :initial-data="currentItem" @submit="handleSubmit" @cancel="closeModal" />
        </template>
        <template #footer><div></div></template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminBlogStore } from '../../stores/adminBlog';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import Modal from '../components/Modal.vue';
import BlogArticleForm from '../components/BlogArticleForm.vue';
import BlogCategoryForm from '../components/BlogCategoryForm.vue';

const blogStore = useAdminBlogStore();
const notificationStore = useAdminNotificationStore();

const activeTab = ref('articles');
const isModalOpen = ref(false);
const modalMode = ref(''); // e.g., 'addArticle', 'editCategory'
const currentItem = ref({});

const articleColumns = [ { key: 'id', label: 'ID' }, { key: 'title', label: 'Title' }, { key: 'category_name', label: 'Category' }, { key: 'is_published', label: 'Status' }, { key: 'actions', label: 'Actions' }];
const categoryColumns = [ { key: 'id', label: 'ID' }, { key: 'name', label: 'Name' }, { key: 'actions', label: 'Actions' }];

const modalTitle = computed(() => {
    if (modalMode.value === 'addArticle') return 'Add New Article';
    if (modalMode.value === 'editArticle') return 'Edit Article';
    if (modalMode.value === 'addCategory') return 'Add New Category';
    if (modalMode.value === 'editCategory') return 'Edit Category';
    return '';
});

onMounted(() => { blogStore.fetchData(); });

const openModal = (mode, item = {}) => {
  modalMode.value = mode;
  currentItem.value = JSON.parse(JSON.stringify(item));
  isModalOpen.value = true;
};

const closeModal = () => { isModalOpen.value = false; };

const handleSubmit = async (data) => {
    let success = false;
    let type = '';
    const isEditing = !!data.id;

    switch(modalMode.value) {
        case 'addArticle':
        case 'editArticle':
            type = 'Article';
            success = isEditing ? await blogStore.updateArticle(data.id, data) : await blogStore.createArticle(data);
            break;
        case 'addCategory':
        case 'editCategory':
            type = 'Category';
            success = isEditing ? await blogStore.updateBlogCategory(data.id, data) : await blogStore.createBlogCategory(data);
            break;
    }

    if (success) {
        closeModal();
        notificationStore.addNotification({ type: 'success', title: `${type} ${isEditing ? 'Updated' : 'Created'}`});
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Save Failed', message: blogStore.error });
    }
};

const handleDelete = async (type, item) => {
    if (!confirm(`Are you sure you want to delete this ${type}?`)) return;
    
    let success = false;
    if (type === 'article') {
        success = await blogStore.deleteArticle(item.id);
    } else if (type === 'category') {
        success = await blogStore.deleteBlogCategory(item.id);
    }

    if (success) {
        notificationStore.addNotification({ type: 'success', title: `${type.charAt(0).toUpperCase() + type.slice(1)} Deleted` });
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Delete Failed', message: blogStore.error });
    }
};

</script>
