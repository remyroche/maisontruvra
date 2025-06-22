// website/source/admin/js/admin_manage_pos.js (Full Script)
document.addEventListener('DOMContentLoaded', () => {
    const posColumns = [
        { header: 'Request ID', key: 'id' },
        { header: 'Company', key: 'company_name' },
        { header: 'User', key: 'user.email' },
        { header: 'Date', key: 'created_at', cell: r => new Date(r.created_at).toLocaleDateString() },
        { header: 'Status', key: 'status', cell: r => `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${r.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' : (r.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800')}">${r.status}</span>`},
        { header: 'Actions', key: 'id', cell: r => {
            if (r.status === 'PENDING') {
                return `
                    <button class="text-indigo-600 hover:text-indigo-900" onclick="approvePOS(${r.id})">Approve</button> |
                    <button class="text-red-600 hover:text-red-900" onclick="openRejectModal(${r.id})">Reject</button>
                `;
            }
            return 'N/A';
        }}
    ];
    
    const fetchPOSRequests = async (page = 1) => {
        const response = await apiClient.get(`/admin/pos?page=${page}`);
        if (!response.ok) throw new Error('Failed to fetch POS requests');
        return response.data;
    };

    new DataTableFactory('pos-table-container', {
        columns: posColumns,
        fetchData: fetchPOSRequests,
        dataKey: 'requests',
        totalKey: 'total_requests'
    });
});

function openRejectModal(requestId) {
    const modal = document.getElementById('reject-pos-modal');
    modal.classList.remove('hidden');
    // Store the ID on the confirm button
    modal.querySelector('#confirm-rejection-btn').dataset.requestId = requestId;
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

document.getElementById('confirm-rejection-btn').addEventListener('click', async (event) => {
    const requestId = event.target.dataset.requestId;
    const reason = document.getElementById('rejection-reason').value;
    if (!reason) {
        alert('Please provide a rejection reason.');
        return;
    }

    try {
        const response = await apiClient.post(`/admin/pos/${requestId}/reject`, { reason });
        if(response.ok) {
            alert('Request rejected successfully.');
            closeModal('reject-pos-modal');
            location.reload(); // Reload the table to show the updated status
        } else {
            throw new Error(response.data.msg || 'Failed to reject request');
        }
    } catch (error) {
        alert(error.message);
    }
});

async function approvePOS(requestId) {
    if(!confirm('Are you sure you want to approve this POS request?')) return;
    try {
        const response = await apiClient.post(`/admin/pos/${requestId}/approve`);
        if(response.ok) {
            alert('Request approved successfully.');
            location.reload();
        } else {
             throw new Error(response.data.msg || 'Failed to approve request');
        }
    } catch(error) {
        alert(error.message);
    }
}
