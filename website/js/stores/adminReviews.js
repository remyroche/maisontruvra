/*
 * FILENAME: website/js/stores/adminReviews.js
 * DESCRIPTION: Pinia store for managing product reviews.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminReviewStore = defineStore('adminReviews', () => {
    const reviews = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchReviews() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.get('/reviews');
            reviews.value = response.data.reviews;
        } catch (err) {
            error.value = 'Failed to fetch reviews.';
            console.error(err);
        } finally {
            isLoading.value = false;
        }
    }
    
    async function updateReviewStatus(id, is_approved) {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await adminApiClient.put(`/reviews/${id}/status`, { is_approved });
            const index = reviews.value.findIndex(r => r.id === id);
            if (index !== -1) reviews.value[index] = response.data.review;
            return true;
        } catch (err) {
            error.value = 'Failed to update review status.';
            return false;
        } finally {
            isLoading.value = false;
        }
    }

    return { reviews, isLoading, error, fetchReviews, updateReviewStatus };
});
