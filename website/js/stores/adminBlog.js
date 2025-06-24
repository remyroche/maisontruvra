/*
 * FILENAME: website/js/stores/adminBlog.js
 * DESCRIPTION: Pinia store for managing blog articles and categories.
 * UPDATED: Added full CRUD functionality for both articles and categories.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminBlogStore = defineStore('adminBlog', () => {
    const articles = ref([]);
    const categories = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchData() {
        isLoading.value = true;
        error.value = null;
        try {
            const [articlesRes, categoriesRes] = await Promise.all([
                adminApiClient.get('/blog/articles'),
                adminApiClient.get('/blog/categories')
            ]);
            articles.value = articlesRes.data.articles;
            categories.value = categoriesRes.data.categories;
        } catch (err) {
            error.value = 'Failed to fetch blog data.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }

    // --- Article Actions ---
    async function createArticle(data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.post('/blog/articles', data);
            articles.value.unshift(response.data.article);
            return true;
        } catch (err) {
            error.value = `Failed to create article: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }
    
    async function updateArticle(id, data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.put(`/blog/articles/${id}`, data);
            const index = articles.value.findIndex(a => a.id === id);
            if (index !== -1) articles.value[index] = response.data.article;
            return true;
        } catch (err) {
            error.value = `Failed to update article: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    async function deleteArticle(id) {
        isLoading.value = true; error.value = null;
        try {
            await adminApiClient.delete(`/blog/articles/${id}`);
            articles.value = articles.value.filter(a => a.id !== id);
            return true;
        } catch (err) {
            error.value = `Failed to delete article: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    // --- Category Actions ---
    async function createBlogCategory(data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.post('/blog/categories', data);
            categories.value.push(response.data.category);
            return true;
        } catch (err) {
            error.value = `Failed to create blog category: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    async function updateBlogCategory(id, data) {
        isLoading.value = true; error.value = null;
        try {
            const response = await adminApiClient.put(`/blog/categories/${id}`, data);
            const index = categories.value.findIndex(c => c.id === id);
            if (index !== -1) categories.value[index] = response.data.category;
            return true;
        } catch (err) {
            error.value = `Failed to update blog category: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

     async function deleteBlogCategory(id) {
        isLoading.value = true; error.value = null;
        try {
            await adminApiClient.delete(`/blog/categories/${id}`);
            categories.value = categories.value.filter(c => c.id !== id);
            return true;
        } catch (err) {
            error.value = `Failed to delete blog category: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally { isLoading.value = false; }
    }

    return { 
        articles, categories, isLoading, error, fetchData, 
        createArticle, updateArticle, deleteArticle,
        createBlogCategory, updateBlogCategory, deleteBlogCategory
    };
});
