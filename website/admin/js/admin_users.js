// website/source/admin/js/admin_users.js

import { adminApi } from './admin_api.js';
import { DataTable } from './components/DataTable.js';
import { showModal, showToast } from '../js/common/ui.js';
import { createDataTable } from './components/DataTableFactory.js';

document.addEventListener('DOMContentLoaded', () => {
    const userColumns = [
        { header: 'ID', cell: user => user.id },
        { header: 'Email', cell: user => user.email },
        { header: 'Full Name', cell: user => `${user.first_name} ${user.last_name}` },
        { header: 'Role', cell: user => `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.role === 'ADMIN' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">${user.role}</span>`},
        { header: 'Status', cell: user => user.is_active ? '<span class="text-green-600">Active</span>' : '<span class="text-gray-500">Inactive</span>' },
        { header: 'Joined', cell: user => new Date(user.created_at).toLocaleDateString() },
        { header: 'Actions', cell: user => `<button class="text-indigo-600 hover:text-indigo-900" onclick="editUser(${user.id})">Edit</button>` }
    ];
    
    // The fetchData function now accepts a page number
    const fetchUsers = async (page = 1) => {
        const response = await apiClient.get(`/admin/users?page=${page}&per_page=15`);
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        return response.data; // The factory expects the full paginated response object
    };

    new DataTableFactory('users-table-container', userColumns, fetchUsers);
});

// Dummy function for demonstration
function editUser(userId) {
    console.log('Editing user:', userId);
    // In a real app, this would open a modal or navigate to an edit page
    alert(`Editing user with ID: ${userId}`);
}
