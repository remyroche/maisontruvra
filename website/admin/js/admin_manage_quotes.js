// website/source/admin/js/admin_manage_quotes.js

import { DataTable } from './components/DataTable.js';
import { adminApi } from './admin_api.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {

    // Configuration for the quotes DataTable
    const tableOptions = {
        apiEndpoint: '/quotes',
        columns: [
            { title: 'ID', dataProperty: 'id' },
            { title: 'User', dataProperty: 'user.full_name' },
            { title: 'Product Name', dataProperty: 'product_name' },
            { title: 'Quantity', dataProperty: 'quantity' },
            { title: 'Status', dataProperty: 'status', render: (quote) => {
                const status = quote.status.toLowerCase();
                let colorClass = 'bg-gray-100 text-gray-800';
                if (status === 'approved') colorClass = 'bg-green-100 text-green-800';
                if (status === 'rejected') colorClass = 'bg-red-100 text-red-800';
                if (status === 'pending') colorClass = 'bg-yellow-100 text-yellow-800';
                return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${colorClass}">${status}</span>`;
            }},
            { title: 'Received', dataProperty: 'created_at', render: (quote) => {
                return new Date(quote.created_at).toLocaleString();
            }},
            { title: 'Actions', dataProperty: 'id', render: (quote) => {
                const isPending = quote.status.toLowerCase() === 'pending';
                return `
                    ${isPending ? `<button class="approve-btn bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded" data-id="${quote.id}">Approve</button>` : ''}
                    ${isPending ? `<button class="reject-btn bg-yellow-500 hover:bg-yellow-600 text-white py-1 px-3 rounded" data-id="${quote.id}">Reject</button>` : ''}
                    <button class="delete-btn bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded" data-id="${quote.id}">Delete</button>
                `;
            }}
        ]
    };

    const quotesTable = new DataTable('quotes-table-container', tableOptions);

    // Attach event listeners for actions using event delegation
    document.getElementById('quotes-table-container').addEventListener('click', function(event) {
        const target = event.target;
        const quoteId = target.dataset.id;
        
        if (target.classList.contains('approve-btn')) {
            handleUpdateStatus(quoteId, 'approved', quotesTable);
        }
        if (target.classList.contains('reject-btn')) {
            handleUpdateStatus(quoteId, 'rejected', quotesTable);
        }
        if (target.classList.contains('delete-btn')) {
            handleDeleteQuote(quoteId, quotesTable);
        }
    });
});

async function handleUpdateStatus(quoteId, status, tableInstance) {
    if (confirm(`Are you sure you want to ${status} this quote?`)) {
        try {
            await adminApi.put(`/quotes/${quoteId}/status`, { status });
            showToast(`Quote status updated to ${status}.`, 'success');
            tableInstance.fetchData();
        } catch (error) {
            showToast(`Error updating quote: ${error.message}`, 'error');
        }
    }
}

async function handleDeleteQuote(quoteId, tableInstance) {
    if (confirm('Are you sure you want to delete this quote?')) {
        try {
            await adminApi.delete(`/quotes/${quoteId}`);
            showToast('Quote deleted successfully.', 'success');
            tableInstance.fetchData();
        } catch (error) {
            showToast(`Error deleting quote: ${error.message}`, 'error');
        }
    }
}
