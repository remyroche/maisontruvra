import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminBlogStore = defineStore('adminBlog', {
  state: () => ({
    articles: [],
    categories: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchArticles() {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/blog/articles');
        this.articles = response.data;
      } catch (e) {
        this.error = 'Failed to fetch articles.';
      } finally {
        this.isLoading = false;
      }
    },
    async createArticle(articleData) {
      try {
        await apiClient.post('/blog/articles', articleData);
        await this.fetchArticles();
      } catch (e) {
        this.error = 'Failed to create article.';
        throw e;
      }
    },
    async updateArticle(id, articleData) {
      try {
        await apiClient.put(`/blog/articles/${id}`, articleData);
        await this.fetchArticles();
      } catch (e) {
        this.error = 'Failed to update article.';
        throw e;
      }
    },
    async deleteArticle(id) {
        try {
            await apiClient.delete(`/blog/articles/${id}`);
            await this.fetchArticles();
        } catch (e) {
            this.error = "Failed to delete article."
        }
    },
    async fetchCategories() {
        this.isLoading = true;
        try {
            const response = await apiClient.get('/blog/categories');
            this.categories = response.data;
        } catch (e) {
            this.error = 'Failed to fetch blog categories.';
        } finally {
            this.isLoading = false;
        }
    },
    async createCategory(categoryData) {
        try {
            await apiClient.post('/blog/categories', categoryData);
            await this.fetchCategories();
        } catch (e) {
            this.error = "Failed to create blog category."
            throw e;
        }
    },
    async updateCategory(id, categoryData) {
        try {
            await apiClient.put(`/blog/categories/${id}`, categoryData);
            await this.fetchCategories();
        } catch(e) {
            this.error = "Failed to update blog category.";
            throw e;
        }
    },
     async deleteCategory(id) {
        try {
            await apiClient.delete(`/blog/categories/${id}`);
            await this.fetchCategories();
        } catch (e) {
            this.error = "Failed to delete blog category."
        }
    },
  },
});
