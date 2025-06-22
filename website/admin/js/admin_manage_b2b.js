// website/source/admin/js/admin_manage_b2b.js

import { adminApi } from './admin_api.js';
import { DataTable } from './components/DataTable.js';
import { showModal, showToast } from '../js/common/ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const columns = [
        { data: 'id', title: 'ID' },
        { data: 'company_name', title: 'Company Name' },
        { data: 'contact_email', title: 'Contact Email' },
        { data: 'status', title: 'Status' },
        { data: 'tier', title: 'Tier' },
        { 
            data: 'id', 
            title: 'Actions', 
            render: (id, rowData) => {
                let buttons = `<button onclick="window.deletePartner(${id})" class="text-red-500 hover:underline ml-2">Delete</button>`;
                if (rowData.status === 'PENDING') {
                    buttons = `<button onclick="window.approvePartner(${id})" class="text-green-500 hover:underline">Approve</button>` + buttons;
                }
                return buttons;
            }
        }
    ];

    const fetchPartners = async () => {
        const response = await adminApi.get('/b2b/partners');
        return response || [];
    };

    const partnersTable = new DataTable('b2b-partners-table', columns, fetchPartners);
    partnersTable.init();

    window.approvePartner = async function(partnerId) {
        const response = await adminApi.post(`/b2b/partners/${partnerId}/approve`);
        if(response && !response.error) {
            showToast('Partner approved successfully!', 'success');
            partnersTable.refresh();
        }
    };
    
    window.deletePartner = function(partnerId) {
        showModal('Confirm Deletion', `Are you sure you want to delete B2B partner ${partnerId}?`,
            async () => {
                const response = await adminApi.delete(`/b2b/partners/${partnerId}`);
                if (response && !response.error) {
                    showToast('Partner deleted successfully.', 'success');
                    partnersTable.refresh();
                }
            }
        );
    };
});

