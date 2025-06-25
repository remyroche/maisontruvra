import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminBlogStore = defineStore('adminBlog', {
  state: () => ({
    posts: [],
    categories: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    // Post Actions
    async fetchPosts(params = {}) {
      this.isLoading = true;
      try {
        const response = await apiClient.get('/blog/posts', { params });
        this.posts = response.data;
      } catch (e) {
        this.error = 'Failed to fetch blog posts.';
      } finally {
        this.isLoading = false;
      }
    },
    async softDeletePost(id) {
        await apiClient.delete(`/blog/posts/${id}`);
        await this.fetchPosts({ include_deleted: true });
    },
    async hardDeletePost(id) {
        await apiClient.delete(`/blog/posts/${id}?hard=true`);
        await this.fetchPosts({ include_deleted: true });
    },
    async restorePost(id) {
        await apiClient.put(`/blog/posts/${id}/restore`);
        await this.fetchPosts({ include_deleted: true });
    },

    // Category Actions
    async fetchCategories(params = {}) {
        this.isLoading = true;
        try {
            const response = await apiClient.get('/blog/categories', { params });
            this.categories = response.data;
        } catch (e) {
            this.error = 'Failed to fetch blog categories.';
        } finally {
            this.isLoading = false;
        }
    },
    async softDeleteCategory(id) {
        await apiClient.delete(`/blog/categories/${id}`);
        await this.fetchCategories({ include_deleted: true });
    },
    async hardDeleteCategory(id) {
        await apiClient.delete(`/blog/categories/${id}?hard=true`);
        await this.fetchCategories({ include_deleted: true });
    },
    async restoreCategory(id) {
        await apiClient.put(`/blog/categories/${id}/restore`);
        await this.fetchCategories({ include_deleted: true });
    },
  },
});
