// website/source/admin/js/admin_manage_loyalty.js

import { adminApi } from './admin_api.js';
import { DataTable } from './components/DataTable.js';
import { showModal, showToast } from '../js/common/ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const columns = [
        { data: 'id', title: 'ID' },
        { data: 'name', title: 'Tier Name' },
        { data: 'points_required', title: 'Points Required' },
        { data: 'reward_multiplier', title: 'Reward Multiplier' },
        { 
            data: 'id', 
            title: 'Actions', 
            render: (id) => `<button onclick="window.editTier(${id})" class="text-blue-500 hover:underline">Edit</button>`
        }
    ];

    const fetchTiers = async () => {
        const response = await adminApi.get('/loyalty/tiers'); 
        return response.tiers || [];
    };

    const tiersTable = new DataTable('loyalty-tiers-table', columns, fetchTiers);
    tiersTable.init();
    
    window.editTier = function(tierId) {
        showToast(`Editing for tier ${tierId} is not yet implemented.`, 'info');
    };

    const configureBtn = document.getElementById('configure-loyalty-btn');
    if (configureBtn) {
        configureBtn.addEventListener('click', () => {
            showModal(
                'Configure Loyalty Settings',
                `<div>
                    <label for="points-per-euro" class="block text-sm font-medium text-gray-700">Points per Euro Spent</label>
                    <input type="number" id="points-per-euro" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" value="10">
                 </div>`,
                () => {
                    const points = document.getElementById('points-per-euro').value;
                    adminApi.post('/loyalty/settings', { points_per_euro: parseFloat(points) })
                        .then(res => {
                            if(res && !res.error) {
                                showToast('Settings updated successfully!', 'success');
                            }
                        });
                }
            );
        });
    }
});
