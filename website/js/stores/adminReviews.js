import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminReviewsStore = defineStore('adminReviews', {
  state: () => ({
    reviews: [],
    isLoading: false,
    error: null,
    statuses: ['pending', 'approved'],
  }),
  actions: {
    async fetchReviews(filters = {}) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/reviews', { params: filters });
        this.reviews = response.data;
      } catch (e) {
        this.error = 'Failed to fetch reviews.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async approveReview(reviewId) {
      try {
        await apiClient.put(`/reviews/${reviewId}/approve`);
        await this.fetchReviews();
      } catch (e) {
        this.error = 'Failed to approve review.';
        console.error(this.error, e);
      }
    },
    async deleteReview(reviewId) {
      try {
        await apiClient.delete(`/reviews/${reviewId}`);
        await this.fetchReviews();
      } catch (e) {
        this.error = 'Failed to delete review.';
        console.error(this.error, e);
      }
    },
  },
});
