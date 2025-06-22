// website/source/admin/js/admin_manage_reviews.js

import { adminApi } from './admin_api.js';
import { DataTable } from './components/DataTable.js';
import { showModal, showToast } from '../js/common/ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const columns = [
        { data: 'id', title: 'ID' },
        { data: 'product_name', title: 'Product' },
        { data: 'user_name', title: 'Author' },
        { data: 'rating', title: 'Rating' },
        { data: 'comment', title: 'Comment', render: (comment) => comment.substring(0, 50) + (comment.length > 50 ? '...' : '') },
        { data: 'status', title: 'Status' },
        { 
            data: 'id', 
            title: 'Actions', 
            render: (id, rowData) => {
                let buttons = `<button onclick="window.deleteReview(${id})" class="text-red-500 hover:underline ml-2">Delete</button>`;
                if (rowData.status === 'PENDING') {
                    buttons = `
                        <button onclick="window.approveReview(${id})" class="text-green-500 hover:underline">Approve</button>
                        <button onclick="window.rejectReview(${id})" class="text-yellow-600 hover:underline ml-2">Reject</button>
                    ` + buttons;
                }
                return buttons;
            }
        }
    ];

    const fetchReviews = async () => {
        const response = await adminApi.get('/reviews');
        return response.reviews || [];
    };

    const reviewsTable = new DataTable('reviews-data-table', columns, fetchReviews);
    reviewsTable.init();

    window.approveReview = async function(reviewId) {
        const response = await adminApi.put(`/reviews/${reviewId}/approve`);
        if(response && !response.error) {
            showToast('Review approved!', 'success');
            reviewsTable.refresh();
        }
    };

    window.rejectReview = async function(reviewId) {
        const response = await adminApi.put(`/reviews/${reviewId}/reject`);
        if(response && !response.error) {
            showToast('Review rejected.', 'info');
            reviewsTable.refresh();
        }
    };

    window.deleteReview = function(reviewId) {
        showModal(
            'Confirm Deletion',
            `Are you sure you want to permanently delete review ${reviewId}?`,
            async () => {
                const response = await adminApi.delete(`/reviews/${reviewId}`);
                if (response && !response.error) {
                    showToast('Review deleted successfully!', 'success');
                    reviewsTable.refresh();
                }
            }
        );
    };
});
