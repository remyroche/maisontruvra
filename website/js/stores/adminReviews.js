import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminReviewsStore = defineStore('adminReviews', {
  state: () => ({
    reviews: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchReviews(params = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/reviews', { params });
        this.reviews = response.data.data; // Assuming paginated
      } catch (e) {
        console.error('Failed to fetch reviews:', e);
        this.error = 'Failed to fetch reviews.';
      } finally {
        this.isLoading = false;
      }
    },
    async approveReview(reviewId) {
        try {
            await apiClient.put(`/reviews/${reviewId}/approve`);
            await this.fetchReviews();
        } catch(e) {
            console.error('Failed to approve review:', e);
            this.error = 'Could not approve the review.';
            throw e;
        }
    },
    async softDeleteReview(reviewId) {
      this.error = null;
      try {
        await apiClient.delete(`/reviews/${reviewId}`);
        await this.fetchReviews();
      } catch (e) {
        this.error = 'Could not soft-delete the review.';
        throw e;
      }
    },
    async hardDeleteReview(reviewId) {
      this.error = null;
      try {
        await apiClient.delete(`/reviews/${reviewId}?hard=true`);
        await this.fetchReviews();
      } catch (e) {
        this.error = 'Could not permanently delete the review.';
        throw e;
      }
    },
    async restoreReview(reviewId) {
      this.error = null;
      try {
        await apiClient.put(`/reviews/${reviewId}/restore`);
        await this.fetchReviews();
      } catch (e) {
        this.error = 'Could not restore the review.';
        throw e;
      }
    },
  },
});
