<template>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Main content: Articles -->
        <div class="md:col-span-2">
            <h1 class="text-2xl font-bold mb-4">Manage Blog Articles</h1>
            <div class="mb-4 text-right">
                <button @click="openArticleModal()" class="bg-green-500 text-white px-4 py-2 rounded">New Article</button>
            </div>
            <!-- Article List -->
             <BaseDataTable :headers="articleHeaders" :items="blogStore.articles">
                 <template #item-actions="{ item }">
                     <button @click="openArticleModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
                     <button @click="deleteArticle(item.id)" class="text-red-600 hover:text-red-900">Delete</button>
                 </template>
            </BaseDataTable>
        </div>

        <!-- Sidebar: Categories -->
        <div>
            <h2 class="text-xl font-bold mb-4">Blog Categories</h2>
            <div class="bg-white p-4 rounded shadow">
                <BlogCategoryForm @save="saveCategory" :key="categoryFormKey" />
                <ul class="mt-4 space-y-2">
                    <li v-for="cat in blogStore.categories" :key="cat.id" class="flex justify-between items-center">
                        {{ cat.name }}
                        <div>
                           <button @click="deleteCategory(cat.id)" class="text-red-500 text-sm">Delete</button>
                        </div>
                    </li>
                </ul>
            </div>
        </div>

        <!-- Article Modal -->
        <Modal :is-open="isArticleModalOpen" @close="closeArticleModal">
            <h2 class="text-xl font-bold mb-4">{{ isEditingArticle ? 'Edit Article' : 'New Article' }}</h2>
            <BlogArticleForm :article="selectedArticle" :categories="blogStore.categories" @save="saveArticle" @cancel="closeArticleModal" />
        </Modal>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminBlogStore } from '@/js/stores/adminBlog';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';
import BlogArticleForm from '@/js/admin/components/BlogArticleform.vue';
import BlogCategoryForm from '@/js/admin/components/BlogCategoryForm.vue';

const blogStore = useAdminBlogStore();

// State for articles
const isArticleModalOpen = ref(false);
const isEditingArticle = ref(false);
const selectedArticle = ref(null);
const articleHeaders = [
    { text: 'Title', value: 'title' },
    { text: 'Category', value: 'category_name' },
    { text: 'Published', value: 'is_published' },
    { text: 'Actions', value: 'actions' },
];

// State for categories
const categoryFormKey = ref(0);


onMounted(() => {
    blogStore.fetchArticles();
    blogStore.fetchCategories();
});

// Article methods
const openArticleModal = (article = null) => {
    if (article) {
        isEditingArticle.value = true;
        selectedArticle.value = { ...article };
    } else {
        isEditingArticle.value = false;
        selectedArticle.value = { title: '', content: '', category_id: null, is_published: false };
    }
    isArticleModalOpen.value = true;
};
const closeArticleModal = () => isArticleModalOpen.value = false;
const saveArticle = async (articleData) => {
    if (isEditingArticle.value) {
        await blogStore.updateArticle(articleData.id, articleData);
    } else {
        await blogStore.createArticle(articleData);
    }
    closeArticleModal();
};
const deleteArticle = (id) => {
    if(confirm('Are you sure you want to delete this article?')) {
        blogStore.deleteArticle(id);
    }
};

// Category methods
const saveCategory = async (categoryData) => {
    await blogStore.createCategory(categoryData);
    categoryFormKey.value++; // Reset the form
};
const deleteCategory = (id) => {
    if(confirm('Are you sure you want to delete this category?')) {
        blogStore.deleteCategory(id);
    }
};
</script>
