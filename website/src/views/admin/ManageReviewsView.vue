<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Reviews</h1>
    <div class="mb-4 flex justify-between items-center">
      <div class="flex items-center space-x-4">
        <select v-model="statusFilter" @change="fetchData" class="border rounded p-2">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
        </select>
        <label class="flex items-center text-sm">
            <input type="checkbox" v-model="includeDeleted" @change="fetchData" class="mr-2 h-4 w-4 rounded">
            Show Deleted
        </label>
      </div>
    </div>
    <div v-if="reviewsStore.isLoading" class="text-center p-4">Loading reviews...</div>
    <div v-if="reviewsStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ reviewsStore.error }}</div>

    <BaseDataTable
      v-if="!reviewsStore.isLoading && reviewsStore.reviews.length"
      :headers="headers"
      :items="reviewsStore.reviews"
    >
        <template #row="{ item }">
            <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                <td v-for="header in headers" :key="header.value" class="px-6 py-4 whitespace-nowrap text-sm">
                   <slot :name="`item-${header.value}`" :item="item">{{ getNestedValue(item, header.value) }}</slot>
                </td>
            </tr>
        </template>
        <template #item-rating="{ item }">{{ '★'.repeat(item.rating) }}</template>
        <template #item-status="{ item }">
             <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="getStatusClass(item.status)">
                {{ item.status }}
            </span>
             <span v-if="item.is_deleted" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-200 text-red-800">Deleted</span>
        </template>
        <template #item-actions="{ item }">
            <div class="flex items-center space-x-2">
                <button v-if="!item.is_deleted && item.status === 'pending'" @click="reviewsStore.approveReview(item.id)" class="text-blue-600 hover:text-blue-900 text-sm">Approve</button>
                <button v-if="!item.is_deleted" @click="confirmDelete(item, 'soft')" class="text-yellow-600 hover:text-yellow-900 text-sm">Soft Delete</button>
                <button v-if="item.is_deleted" @click="restoreReview(item.id)" class="text-green-600 hover:text-green-900 text-sm">Restore</button>
                <button @click="confirmDelete(item, 'hard')" class="text-red-600 hover:text-red-900 text-sm">Hard Delete</button>
            </div>
        </template>
    </BaseDataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminReviewsStore } from '@/js/stores/adminReviews';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const reviewsStore = useAdminReviewsStore();
const statusFilter = ref('');
const includeDeleted = ref(false);

const headers = [
  { text: 'Product', value: 'product.name' },
  { text: 'User', value: 'user.first_name' },
  { text: 'Rating', value: 'rating' },
  { text: 'Status', value: 'status' },
  { text: 'Comment', value: 'comment' },
  { text: 'Actions', value: 'actions' },
];

const fetchData = () => {
    reviewsStore.fetchReviews({
        status: statusFilter.value,
        include_deleted: includeDeleted.value,
    });
};

onMounted(fetchData);

const getNestedValue = (item, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], item);
}

const getStatusClass = (status) => {
    const classes = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'approved': 'bg-green-100 text-green-800',
        'rejected': 'bg-red-100 text-red-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
};

const confirmDelete = (review, type) => {
  const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
  if (window.confirm(`Are you sure you want to ${action} this review?`)) {
    const deleteAction = type === 'soft' ? reviewsStore.softDeleteReview : reviewsStore.hardDeleteReview;
    deleteAction(review.id);
  }
};

const restoreReview = (reviewId) => {
  if (window.confirm(`Are you sure you want to restore this review?`)) {
    reviewsStore.restoreReview(reviewId);
  }
};
</script>
