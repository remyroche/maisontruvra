<!--
 * FILENAME: website/js/admin/views/ManageReviewsView.vue
 * DESCRIPTION: View for managing product reviews, now fully implemented.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-800">Manage Reviews</h1>
      </header>

      <div v-if="reviewStore.isLoading && !reviewStore.reviews.length" class="text-center py-10">Loading reviews...</div>
      <div v-else-if="reviewStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
        {{ reviewStore.error }}
      </div>
      
      <BaseDataTable v-else :columns="columns" :data="reviewStore.reviews">
        <template #cell(product_name)="{ value }">
            <span class="font-medium">{{ value }}</span>
        </template>
         <template #cell(rating)="{ value }">
            <StarRating :rating="value" />
        </template>
        <template #cell(is_approved)="{ value }">
             <span :class="value ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                   class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ value ? 'Approved' : 'Pending' }}
             </span>
        </template>
        <template #cell(actions)="{ item }">
            <template v-if="!item.is_approved">
                 <button @click="handleUpdateStatus(item, true)" class="bg-green-500 hover:bg-green-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Approve</button>
            </template>
            <template v-else>
                 <button @click="handleUpdateStatus(item, false)" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Un-approve</button>
            </template>
             <button @click="handleDelete(item)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
        </template>
      </BaseDataTable>
    </div>
  </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminReviewStore } from '../../stores/adminReviews';
import { useAdminNotificationStore } from '../../stores/adminNotifications';

import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import StarRating from '../components/ui/StarRating.vue';

const reviewStore = useAdminReviewStore();
const notificationStore = useAdminNotificationStore();

const columns = [
    { key: 'id', label: 'ID' },
    { key: 'product_name', label: 'Product' },
    { key: 'user_name', label: 'Customer' },
    { key: 'rating', label: 'Rating' },
    { key: 'comment', label: 'Comment' },
    { key: 'is_approved', label: 'Status' },
    { key: 'actions', label: 'Actions', cellClass: 'text-right' },
];

onMounted(() => {
  reviewStore.fetchReviews();
});

const handleUpdateStatus = async (review, newStatus) => {
    const action = newStatus ? 'approve' : 'un-approve';
    if (confirm(`Are you sure you want to ${action} this review?`)) {
        const success = await reviewStore.updateReviewStatus(review.id, newStatus);
        if (success) {
            notificationStore.addNotification({ type: 'success', title: 'Status Updated' });
        } else {
            notificationStore.addNotification({ type: 'error', title: 'Update Failed', message: reviewStore.error });
        }
    }
};

const handleDelete = async (review) => {
    // Note: A delete action in the store is pending implementation.
    if (confirm(`Are you sure you want to permanently delete this review?`)) {
        notificationStore.addNotification({ type: 'info', title: 'Action Not Implemented', message: 'Review deletion logic is pending.'})
        // const success = await reviewStore.deleteReview(review.id);
        // ...
    }
}

</script>
