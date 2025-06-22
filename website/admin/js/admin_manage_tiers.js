// website/source/admin/js/admin_manage_tiers.js

import { DataTable } from './components/DataTable.js';
import { adminApi } from './admin_api.js';
import { showToast } from './admin_ui.js';


document.addEventListener('DOMContentLoaded', () => {
    const api = new AdminAPI();
    const form = document.getElementById('tiers-form');
    const container = document.getElementById('tiers-container');
    const loadingIndicator = document.getElementById('tiers-loading');
    let tiersCache = [];

    const createTierCard = (tier) => {
        // Renaming for display based on the new names
        const tierNames = {
            collaborateur: 'Collaborateur (Base Tier)',
            architecte: 'Partenaire',
            visionnaire: 'Associé',
            ambassadeur: 'Ambassadeur'
        };

        let spendThresholdInput = '';
        let discountLabel = 'Discount (%)';

        if (tier.key_name === 'architecte' || tier.key_name === 'visionnaire') {
            spendThresholdInput = `
                <div>
                    <label for="spend-rank-${tier.id}" class="block text-sm font-medium text-brand-dark-gray">Qualification: Top X% Spenders</label>
                    <input type="number" id="spend-rank-${tier.id}" value="${tier.spend_rank_threshold || ''}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-gold focus:ring-brand-gold sm:text-sm">
                </div>`;
            discountLabel = 'Additional Discount (%)';
        } else if (tier.key_name === 'collaborateur'){
            discountLabel = 'Base Professional Discount (%)';
        }


        return `
            <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-brand-gold">
                <h2 class="text-xl font-serif text-brand-burgundy mb-4">${tierNames[tier.key_name] || tier.display_name}</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="discount-${tier.id}" class="block text-sm font-medium text-brand-dark-gray">${discountLabel}</label>
                        <input type="number" step="0.5" id="discount-${tier.id}" value="${tier.discount_percentage}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-gold focus:ring-brand-gold sm:text-sm" required>
                    </div>
                    ${spendThresholdInput}
                </div>
                ${tier.key_name === 'ambassadeur' ? '<p class="text-sm text-gray-500 mt-4">Note: Ambassadeurs also receive all benefits of the Partenaire Visionnaire tier.</p>' : ''}
            </div>`;
    };

    const loadTiers = async () => {
        try {
            loadingIndicator.style.display = 'block';
            form.classList.add('hidden');
            
            tiersCache = await api.get('/admin/api/loyalty/b2b-tiers');
            container.innerHTML = tiersCache.map(createTierCard).join('');
            
            loadingIndicator.style.display = 'none';
            form.classList.remove('hidden');
        } catch (error) {
            loadingIndicator.textContent = 'Error: Could not load tier settings.';
            console.error('Failed to load tiers:', error);
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const updatedTiers = tiersCache.map(tier => {
            const updatedTier = {
                id: tier.id,
                discount_percentage: document.getElementById(`discount-${tier.id}`).value,
            };
            const spendRankInput = document.getElementById(`spend-rank-${tier.id}`);
            if (spendRankInput) {
                updatedTier.spend_rank_threshold = spendRankInput.value;
            }
            return updatedTier;
        });

        try {
            const response = await api.put('/admin/api/loyalty/b2b-tiers', updatedTiers);
            alert('B2B tier settings updated successfully!');
            await loadTiers(); // Refresh data
        } catch (error) {
            alert('Error: Could not save settings.');
            console.error('Failed to update tiers:', error);
        }
    });

    loadTiers();
});

document.addEventListener('DOMContentLoaded', () => {

    const tableOptions = {
        apiEndpoint: '/loyalty/tiers/manage',
        columns: [
            { title: 'ID', dataProperty: 'id' },
            { title: 'Tier Name', dataProperty: 'name' },
            { title: 'Discount (%)', dataProperty: 'discount_percentage' },
            { title: 'Min Points', dataProperty: 'min_points' },
            { title: 'Actions', dataProperty: 'id', render: (tier) => {
                return `
                    <button class="edit-btn bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded" data-id="${tier.id}">Edit</button>
                    <button class="delete-btn bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded" data-id="${tier.id}">Delete</button>
                `;
            }}
        ]
    };

    const tiersTable = new DataTable('tiers-table-container', tableOptions);

    // --- Modal and Form Handling ---
    const tierModal = document.getElementById('tier-modal');
    const tierForm = document.getElementById('tier-form');
    const closeModalBtn = document.querySelector('#tier-modal .close-modal');

    document.getElementById('add-tier-btn').addEventListener('click', () => {
        tierForm.reset();
        document.getElementById('tier-id').value = '';
        tierModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => {
        tierModal.classList.add('hidden');
    });
    
    document.getElementById('tiers-table-container').addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-btn')) {
            handleEditTier(event.target.dataset.id);
        }
        if (event.target.classList.contains('delete-btn')) {
            handleDeleteTier(event.target.dataset.id);
        }
    });

    tierForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tierId = document.getElementById('tier-id').value;
        const data = {
            name: document.getElementById('name').value,
            discount_percentage: parseFloat(document.getElementById('discount_percentage').value),
            min_points: parseInt(document.getElementById('min_points').value, 10)
        };
        
        const endpoint = tierId ? `/loyalty/tiers/${tierId}` : '/loyalty/tiers';
        const method = tierId ? 'PUT' : 'POST';

        try {
            await adminApi.request(endpoint, method, data);
            showToast(`Tier ${tierId ? 'updated' : 'created'} successfully`, 'success');
            tierModal.classList.add('hidden');
            tiersTable.fetchData();
        } catch (error) {
            showToast(`Error saving tier: ${error.message}`, 'error');
        }
    });

    async function handleEditTier(tierId) {
        try {
            // NOTE: This assumes a GET /tiers/<id> endpoint exists. Let's add it.
            const tier = await adminApi.get(`/loyalty/tiers/${tierId}`); 
            document.getElementById('tier-id').value = tier.id;
            document.getElementById('name').value = tier.name;
            document.getElementById('discount_percentage').value = tier.discount_percentage;
            document.getElementById('min_points').value = tier.min_points;
            tierModal.classList.remove('hidden');
        } catch (error) {
            showToast('Error fetching tier details.', 'error');
        }
    }

    async function handleDeleteTier(tierId) {
        if (confirm('Are you sure you want to delete this tier? This might affect B2B users currently in this tier.')) {
            try {
                await adminApi.delete(`/loyalty/tiers/${tierId}`);
                showToast('Tier deleted successfully', 'success');
                tiersTable.fetchData();
            } catch (error) {
                showToast(`Error deleting tier: ${error.message}`, 'error');
            }
        }
    }
});
