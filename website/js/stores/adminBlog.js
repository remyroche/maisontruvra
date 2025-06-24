/*
 * FILENAME: website/js/stores/adminBlog.js
 * DESCRIPTION: Pinia store for managing blog articles and their categories.
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

    async function createArticle(data) {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.post('/blog/articles', data);
            articles.value.unshift(response.data.article);
            return true;
        } catch (err) {
            error.value = `Failed to create article: ${err.response?.data?.message || 'error'}`;
            return false;
        } finally {
            isLoading.value = false;
        }
    }
    // ... other actions for update/delete articles and categories

    return { articles, categories, isLoading, error, fetchData, createArticle };
});
