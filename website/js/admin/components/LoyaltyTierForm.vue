<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Product Reviews</h1>

    <div class="mb-4">
        <select v-model="statusFilter" @change="applyFilters" class="border rounded p-2">
            <option value="">All Reviews</option>
            <option v-for="status in reviewsStore.statuses" :key="status" :value="status">{{ status }}</option>
        </select>
    </div>

    <div v-if="reviewsStore.isLoading" class="text-center p-4">Loading reviews...</div>
    <div v-if="reviewsStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ reviewsStore.error }}</div>

    <div v-if="!reviewsStore.isLoading" class="space-y-4">
        <div v-for="review in reviewsStore.reviews" :key="review.id" class="bg-white p-4 rounded-lg shadow">
            <div class="flex justify-between items-start">
                <div>
                    <p class="font-semibold">{{ review.product_name }}</p>
                    <p class="text-sm text-gray-600">by {{ review.user_name }}</p>
                    <StarRating :rating="review.rating" class="mt-1" />
                </div>
                <div class="text-right">
                     <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="statusClass(review.status)">
                        {{ review.status }}
                    </span>
                    <p class="text-xs text-gray-500 mt-1">{{ new Date(review.created_at).toLocaleDateString() }}</p>
                </div>
            </div>
            <p class="mt-2 text-gray-700">{{ review.comment }}</p>
            <div class="mt-4 flex justify-end space-x-2">
                <button v-if="review.status === 'pending'" @click="approveReview(review.id)" class="bg-green-500 text-white px-3 py-1 text-sm rounded">Approve</button>
                <button @click="deleteReview(review.id)" class="bg-red-500 text-white px-3 py-1 text-sm rounded">Delete</button>
            </div>
        </div>
        <div v-if="!reviewsStore.reviews.length" class="text-center text-gray-500 py-8">
            No reviews found for this filter.
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminReviewsStore } from '@/js/stores/adminReviews';
import StarRating from '@/js/admin/components/ui/StarRating.vue';

const reviewsStore = useAdminReviewsStore();
const statusFilter = ref('');

onMounted(() => {
    reviewsStore.fetchReviews();
});

const applyFilters = () => {
    reviewsStore.fetchReviews({ status: statusFilter.value });
};

const approveReview = (id) => {
    reviewsStore.approveReview(id);
};

const deleteReview = (id) => {
    if (confirm('Are you sure you want to delete this review permanently?')) {
        reviewsStore.deleteReview(id);
    }
};

const statusClass = (status) => {
  return status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
};
</script>
