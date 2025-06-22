import { checkAdminAuth, loadAdminHeader } from './admin_common.js';
import { showToast } from './admin_ui.js';
import { config } from './admin_config.js';
import { AdminApi } from './admin_api.js';

document.addEventListener('DOMContentLoaded', () => {
    const orderColumns = [
        { header: 'Order ID', key: 'id', cell: o => `<a href="#" onclick="viewOrder(${o.id})" class="text-indigo-600 font-bold">#${o.id}</a>` },
        { header: 'Customer', key: 'user.email' },
        { header: 'Date', key: 'created_at', cell: o => new Date(o.created_at).toLocaleString() },
        { header: 'Total', key: 'total_price', cell: o => `$${parseFloat(o.total_price).toFixed(2)}` },
        { header: 'Status', key: 'status', cell: o => `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">${o.status}</span>`},
        { header: 'Actions', key: 'id', cell: o => `<button class="text-indigo-600 hover:text-indigo-900" onclick="viewOrder(${o.id})">View Details</button>` }
    ];
    
    const fetchOrders = async (page = 1) => {
        const response = await apiClient.get(`/admin/orders?page=${page}&per_page=15`);
        if (!response.ok) throw new Error('Failed to fetch orders');
        return response.data;
    };

    new DataTableFactory('orders-table-container', {
        columns: orderColumns,
        fetchData: fetchOrders,
        dataKey: 'orders',
        totalKey: 'total_orders'
    });
});

function viewOrder(orderId) {
    // In a real app, this would navigate to a detailed order page
    alert(`Viewing details for order ID: ${orderId}`);
}

document.addEventListener('DOMContentLoaded', async () => {
    await checkAdminAuth();
    const api = new AdminApi(config.api_url, localStorage.getItem('admin_token'));
    await loadAdminHeader();

    const tableBody = document.getElementById('orders-table-body');
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');
    const searchBtn = document.getElementById('search-btn');
    const paginationControls = document.getElementById('pagination-controls');

    // Modal elements
    const modal = document.getElementById('order-detail-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalContentContainer = document.getElementById('modal-content-container');
    const modalContentLoading = document.getElementById('modal-content-loading');
    const modalOrderReference = document.getElementById('modal-order-reference');
    const modalCustomerDetails = document.getElementById('modal-customer-details');
    const modalOrderSummary = document.getElementById('modal-order-summary');
    const modalOrderItems = document.getElementById('modal-order-items');
    const modalOrderNotes = document.getElementById('modal-order-notes');
    const newNoteTextarea = document.getElementById('new-note-textarea');
    const addNoteBtn = document.getElementById('add-note-btn');

    let currentPage = 1;
    let currentOrderId = null;

    const ORDER_STATUSES = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED'];

    function populateStatusFilter() {
        ORDER_STATUSES.forEach(status => {
            const option = document.createElement('option');
            option.value = status;
            option.textContent = status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
            statusFilter.appendChild(option);
        });
    }
    
    async function fetchOrders(page = 1) {
        currentPage = page;
        const searchTerm = searchInput.value.trim();
        const status = statusFilter.value;
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center p-4">Loading...</td></tr>`;

        try {
            const data = await api.getOrders({ page, per_page: 10, search: searchTerm, status });
            renderOrdersTable(data.orders);
            renderPagination(data);
        } catch (error) {
            console.error('Failed to fetch orders:', error);
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center p-4 text-red-500">Failed to load orders.</td></tr>`;
            showToast('Failed to load orders', true);
        }
    }

    function renderOrdersTable(orders) {
        if (!orders || orders.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center p-4">No orders found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = orders.map(order => `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${order.reference}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${order.user?.email || 'N/A'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(order.created_at).toLocaleDateString()}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">€${order.total_amount.toFixed(2)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${order.status}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button class="view-order-btn text-indigo-600 hover:text-indigo-900" data-order-id="${order.id}">View</button>
                </td>
            </tr>
        `).join('');
    }
    
    function renderPagination(data) {
        // Implementation for pagination controls
    }
    
    async function openOrderDetailModal(orderId) {
        currentOrderId = orderId;
        modal.classList.remove('hidden');
        modalContentContainer.classList.add('hidden');
        modalContentLoading.classList.remove('hidden');

        try {
            const order = await api.getOrderById(orderId);
            modalOrderReference.textContent = order.reference;
            
            // Render details
            modalCustomerDetails.innerHTML = `
                <h4 class="font-semibold text-gray-600 mb-2">Customer</h4>
                <p>${order.user.first_name || ''} ${order.user.last_name || ''}</p>
                <p>${order.user.email}</p>
            `;
            modalOrderSummary.innerHTML = `
                <h4 class="font-semibold text-gray-600 mb-2">Summary</h4>
                <p><strong>Status:</strong> ${order.status}</p>
                <p><strong>Total:</strong> €${order.total_amount.toFixed(2)}</p>
            `;
            
            renderOrderItems(order.items);
            renderOrderNotes(order.notes);

            modalContentContainer.classList.remove('hidden');
        } catch (error) {
            console.error('Failed to fetch order details:', error);
            showToast('Could not load order details.', true);
            modalContentContainer.innerHTML = `<p class="text-red-500 text-center">Failed to load details.</p>`;
        } finally {
            modalContentLoading.classList.add('hidden');
        }
    }

    function renderOrderItems(items) {
        modalOrderItems.innerHTML = `
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50"><tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                </tr></thead>
                <tbody class="bg-white divide-y divide-gray-200">
                ${items.map(item => `
                    <tr>
                        <td class="px-4 py-2 text-sm">${item.product_variant?.product?.name || 'N/A'} (${item.product_variant?.name || 'N/A'})</td>
                        <td class="px-4 py-2 text-sm">${item.quantity}</td>
                        <td class="px-4 py-2 text-sm">€${item.price.toFixed(2)}</td>
                    </tr>
                `).join('')}
                </tbody>
            </table>
        `;
    }

    function renderOrderNotes(notes) {
        if (!notes || notes.length === 0) {
            modalOrderNotes.innerHTML = `<p class="text-sm text-gray-500 text-center">No notes for this order.</p>`;
            return;
        }
        modalOrderNotes.innerHTML = notes.map(note => `
            <div class="bg-white p-3 rounded-md border">
                <p class="text-sm text-gray-800">${note.note}</p>
                <p class="text-xs text-gray-500 mt-1">By ${note.author} on ${new Date(note.created_at).toLocaleString()}</p>
            </div>
        `).join('');
    }
    
    async function handleAddNote() {
        const noteText = newNoteTextarea.value.trim();
        if (!noteText) {
            showToast('Note cannot be empty.', true);
            return;
        }

        addNoteBtn.disabled = true;
        addNoteBtn.textContent = 'Adding...';

        try {
            const newNote = await api.addOrderNote(currentOrderId, noteText);
            showToast('Note added successfully!');
            newNoteTextarea.value = '';
            // Prepend new note to the list for immediate feedback
            const noteHtml = `
                <div class="bg-white p-3 rounded-md border">
                    <p class="text-sm text-gray-800">${newNote.note}</p>
                    <p class="text-xs text-gray-500 mt-1">By ${newNote.author} on ${new Date(newNote.created_at).toLocaleString()}</p>
                </div>
            `;
            if (modalOrderNotes.querySelector('p')) { // If it was empty
                 modalOrderNotes.innerHTML = noteHtml;
            } else {
                 modalOrderNotes.insertAdjacentHTML('afterbegin', noteHtml);
            }
           
        } catch (error) {
            console.error('Failed to add note:', error);
            showToast('Failed to add note.', true);
        } finally {
            addNoteBtn.disabled = false;
            addNoteBtn.textContent = 'Add Note';
        }
    }

    function closeModal() {
        modal.classList.add('hidden');
        currentOrderId = null;
    }

    // Event Listeners
    searchBtn.addEventListener('click', () => fetchOrders(1));
    tableBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-order-btn')) {
            openOrderDetailModal(e.target.dataset.orderId);
        }
    });
    modalCloseBtn.addEventListener('click', closeModal);
    addNoteBtn.addEventListener('click', handleAddNote);


    // Initial Load
    populateStatusFilter();
    fetchOrders();
});
